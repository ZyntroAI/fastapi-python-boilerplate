script_content = '''#!/usr/bin/env python3
"""
validate_ci_env.py — Pre-deployment validation for FastAPI + Postgres + Redis CI/CD pipelines.

Run this script locally or in a pre-flight CI job to catch connection and configuration
errors BEFORE they hit your main test/deploy workflow.

Usage:
    python scripts/validate_ci_env.py

Exit codes:
    0 — All checks passed
    1 — One or more checks failed
"""

from __future__ import annotations

import argparse
import asyncio
import os
import socket
import sys
import time
import urllib.parse
from dataclasses import dataclass, field
from typing import List

# Optional deps — graceful degradation if not installed
try:
    import asyncpg
    HAS_ASYNCpg = True
except ImportError:
    HAS_ASYNCpg = False

try:
    import redis.asyncio as aioredis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

try:
    import sqlalchemy
    from sqlalchemy.ext.asyncio import create_async_engine
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    duration_ms: float = 0.0
    suggestion: str = ""


class ValidationRunner:
    def __init__(self, verbose: bool = False, timeout: float = 10.0):
        self.verbose = verbose
        self.timeout = timeout
        self.results: List[CheckResult] = []

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(f"[DEBUG] {msg}")

    def _add(self, result: CheckResult) -> None:
        self.results.append(result)
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"{status}  {result.name}  ({result.duration_ms:.0f}ms)")
        if not result.passed and result.suggestion:
            print(f"   💡 {result.suggestion}")
        if not result.passed and result.message:
            print(f"   📝 {result.message}")

    # ------------------------------------------------------------------
    # 1. Environment Variable Validation
    # ------------------------------------------------------------------
    def check_env_vars(self) -> None:
        """Verify all required environment variables are present and non-empty."""
        start = time.perf_counter()
        required = [
            "DATABASE_URL",
            "REDIS_URL",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_DB",
        ]
        optional_but_recommended = [
            "POSTGRES_HOST",
            "POSTGRES_PORT",
            "REDIS_HOST",
            "REDIS_PORT",
        ]

        missing = [v for v in required if not os.getenv(v)]
        empty = [v for v in required if os.getenv(v) == ""]

        passed = not missing and not empty
        msg = ""
        if missing:
            msg += f"Missing required vars: {', '.join(missing)}. "
        if empty:
            msg += f"Empty required vars: {', '.join(empty)}. "

        suggestion = (
            "Set missing vars in your .env file or GitHub Actions 'env' block. "
            "For CI, use: env:\\n  DATABASE_URL: postgresql+asyncpg://..."
            if not passed else ""
        )

        self._add(CheckResult(
            name="Environment Variables",
            passed=passed,
            message=msg,
            duration_ms=(time.perf_counter() - start) * 1000,
            suggestion=suggestion,
        ))

    # ------------------------------------------------------------------
    # 2. DATABASE_URL Parse & Schema Validation
    # ------------------------------------------------------------------
    def check_database_url(self) -> None:
        """Validate that DATABASE_URL is well-formed and uses async driver."""
        start = time.perf_counter()
        url = os.getenv("DATABASE_URL", "")
        if not url:
            self._add(CheckResult(
                name="DATABASE_URL Parse",
                passed=False,
                message="DATABASE_URL is not set.",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion="Export DATABASE_URL before running this script.",
            ))
            return

        try:
            parsed = urllib.parse.urlparse(url)
        except Exception as exc:
            self._add(CheckResult(
                name="DATABASE_URL Parse",
                passed=False,
                message=f"Invalid URL: {exc}",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion="Format: postgresql+asyncpg://user:pass@host:port/db",
            ))
            return

        issues = []
        if parsed.scheme not in ("postgresql+asyncpg", "postgresql+psycopg"):
            issues.append(
                f"Scheme is '{parsed.scheme}' — prefer 'postgresql+asyncpg' for FastAPI async."
            )
        if not parsed.hostname:
            issues.append("Missing hostname.")
        if not parsed.path or parsed.path == "/":
            issues.append("Missing database name in path.")

        passed = not issues
        self._add(CheckResult(
            name="DATABASE_URL Parse",
            passed=passed,
            message="; ".join(issues) if issues else "URL is well-formed.",
            duration_ms=(time.perf_counter() - start) * 1000,
            suggestion="Use postgresql+asyncpg://user:pass@localhost:5432/dbname" if issues else "",
        ))

    # ------------------------------------------------------------------
    # 3. Postgres TCP Reachability
    # ------------------------------------------------------------------
    def check_postgres_tcp(self) -> None:
        """Check if Postgres host:port is reachable via TCP."""
        start = time.perf_counter()
        host = os.getenv("POSTGRES_HOST") or os.getenv("DATABASE_URL", "")
        port = os.getenv("POSTGRES_PORT", "5432")

        if not host and os.getenv("DATABASE_URL"):
            try:
                parsed = urllib.parse.urlparse(os.getenv("DATABASE_URL"))
                host = parsed.hostname or "localhost"
                port = str(parsed.port or 5432)
            except Exception:
                host = "localhost"
                port = "5432"
        elif not host:
            host = "localhost"
            port = "5432"

        try:
            sock = socket.create_connection((host, int(port)), timeout=self.timeout)
            sock.close()
            self._add(CheckResult(
                name="Postgres TCP Reachable",
                passed=True,
                message=f"{host}:{port} is open.",
                duration_ms=(time.perf_counter() - start) * 1000,
            ))
        except Exception as exc:
            self._add(CheckResult(
                name="Postgres TCP Reachable",
                passed=False,
                message=f"Cannot connect to {host}:{port}: {exc}",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion=(
                    "1) Is Postgres running? 2) Check firewall rules. "
                    "3) In GitHub Actions, use 'services:' block with healthcheck. "
                    "4) Ensure host matches service name (e.g., 'postgres' not 'localhost')."
                ),
            ))

    # ------------------------------------------------------------------
    # 4. Postgres Authentication & Permissions
    # ------------------------------------------------------------------
    async def check_postgres_auth(self) -> None:
        """Attempt to connect to Postgres and run a simple query."""
        start = time.perf_counter()
        if not HAS_ASYNCpg:
            self._add(CheckResult(
                name="Postgres Auth & Query",
                passed=False,
                message="asyncpg not installed. Run: uv add --dev asyncpg",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion="Add asyncpg to your dev dependencies.",
            ))
            return

        url = os.getenv("DATABASE_URL", "")
        if not url:
            self._add(CheckResult(
                name="Postgres Auth & Query",
                passed=False,
                message="DATABASE_URL missing.",
                duration_ms=(time.perf_counter() - start) * 1000,
            ))
            return

        try:
            conn = await asyncpg.connect(url, timeout=self.timeout)
            row = await conn.fetchrow("SELECT 1 AS check_val, version() AS v")
            await conn.close()
            self._add(CheckResult(
                name="Postgres Auth & Query",
                passed=True,
                message=f"Connected. Server: {row['v'][:40]}...",
                duration_ms=(time.perf_counter() - start) * 1000,
            ))
        except asyncpg.InvalidCatalogNameError as exc:
            self._add(CheckResult(
                name="Postgres Auth & Query",
                passed=False,
                message=f"Database does not exist: {exc}",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion="Create the DB first or check your DATABASE_URL path component.",
            ))
        except asyncpg.PostgresError as exc:
            self._add(CheckResult(
                name="Postgres Auth & Query",
                passed=False,
                message=f"Postgres error: {exc}",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion="Check username/password and pg_hba.conf settings.",
            ))
        except Exception as exc:
            self._add(CheckResult(
                name="Postgres Auth & Query",
                passed=False,
                message=f"Connection failed: {exc}",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion="Verify service container is healthy before running tests.",
            ))

    # ------------------------------------------------------------------
    # 5. Redis TCP Reachability
    # ------------------------------------------------------------------
    def check_redis_tcp(self) -> None:
        """Check if Redis host:port is reachable via TCP."""
        start = time.perf_counter()
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))

        try:
            sock = socket.create_connection((host, port), timeout=self.timeout)
            sock.close()
            self._add(CheckResult(
                name="Redis TCP Reachable",
                passed=True,
                message=f"{host}:{port} is open.",
                duration_ms=(time.perf_counter() - start) * 1000,
            ))
        except Exception as exc:
            self._add(CheckResult(
                name="Redis TCP Reachable",
                passed=False,
                message=f"Cannot connect to {host}:{port}: {exc}",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion=(
                    "1) Is Redis running? 2) In GitHub Actions, use 'services:' with redis:alpine. "
                    "3) Hostname should be 'redis' when using service containers."
                ),
            ))

    # ------------------------------------------------------------------
    # 6. Redis Authentication & PING
    # ------------------------------------------------------------------
    async def check_redis_auth(self) -> None:
        """Attempt to connect to Redis and run PING."""
        start = time.perf_counter()
        if not HAS_REDIS:
            self._add(CheckResult(
                name="Redis Auth & PING",
                passed=False,
                message="redis-py not installed. Run: uv add --dev redis",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion="Add redis to your dev dependencies.",
            ))
            return

        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        password = os.getenv("REDIS_PASSWORD") or None

        try:
            r = aioredis.Redis(
                host=host,
                port=port,
                password=password,
                socket_connect_timeout=self.timeout,
                socket_timeout=self.timeout,
                decode_responses=True,
            )
            pong = await r.ping()
            info = await r.info("server")
            await r.close()
            self._add(CheckResult(
                name="Redis Auth & PING",
                passed=pong,
                message=f"PING={pong}, Redis v{info.get('redis_version', 'unknown')}",
                duration_ms=(time.perf_counter() - start) * 1000,
            ))
        except Exception as exc:
            self._add(CheckResult(
                name="Redis Auth & PING",
                passed=False,
                message=f"Redis connection failed: {exc}",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion="Check Redis password, host, and that the container is healthy.",
            ))

    # ------------------------------------------------------------------
    # 7. SQLAlchemy Engine Sanity (if available)
    # ------------------------------------------------------------------
    async def check_sqlalchemy_engine(self) -> None:
        """Verify SQLAlchemy async engine can be created and connect."""
        start = time.perf_counter()
        if not HAS_SQLALCHEMY:
            self._add(CheckResult(
                name="SQLAlchemy Engine",
                passed=False,
                message="SQLAlchemy not installed.",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion="Run: uv add --dev sqlalchemy[asyncio] asyncpg",
            ))
            return

        url = os.getenv("DATABASE_URL", "")
        if not url:
            self._add(CheckResult(
                name="SQLAlchemy Engine",
                passed=False,
                message="DATABASE_URL missing.",
                duration_ms=(time.perf_counter() - start) * 1000,
            ))
            return

        try:
            engine = create_async_engine(url, pool_pre_ping=True, echo=False)
            from sqlalchemy import text
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                _ = result.scalar()
            await engine.dispose()
            self._add(CheckResult(
                name="SQLAlchemy Engine",
                passed=True,
                message="Engine created and query succeeded.",
                duration_ms=(time.perf_counter() - start) * 1000,
            ))
        except Exception as exc:
            self._add(CheckResult(
                name="SQLAlchemy Engine",
                passed=False,
                message=f"Engine failure: {exc}",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion="Check driver compatibility (asyncpg vs psycopg) and connection string.",
            ))

    # ------------------------------------------------------------------
    # 8. Alembic Configuration Sanity
    # ------------------------------------------------------------------
    def check_alembic_config(self) -> None:
        """Verify alembic.ini exists and points to a valid script_location."""
        start = time.perf_counter()
        ini_path = "alembic.ini"
        if not os.path.exists(ini_path):
            self._add(CheckResult(
                name="Alembic Config",
                passed=False,
                message=f"{ini_path} not found in CWD ({os.getcwd()}).",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion="Run 'alembic init alembic' or ensure CWD is project root.",
            ))
            return

        import configparser
        config = configparser.ConfigParser()
        config.read(ini_path)

        try:
            script_loc = config.get("alembic", "script_location")
            if not os.path.isdir(script_loc):
                self._add(CheckResult(
                    name="Alembic Config",
                    passed=False,
                    message=f"script_location '{script_loc}' does not exist.",
                    duration_ms=(time.perf_counter() - start) * 1000,
                    suggestion="Fix script_location in alembic.ini or create the directory.",
                ))
                return
        except Exception as exc:
            self._add(CheckResult(
                name="Alembic Config",
                passed=False,
                message=f"Error reading alembic.ini: {exc}",
                duration_ms=(time.perf_counter() - start) * 1000,
            ))
            return

        self._add(CheckResult(
            name="Alembic Config",
            passed=True,
            message=f"alembic.ini OK, script_location='{script_loc}'.",
            duration_ms=(time.perf_counter() - start) * 1000,
        ))

    # ------------------------------------------------------------------
    # 9. pyproject.toml / uv.lock Consistency
    # ------------------------------------------------------------------
    def check_pyproject_lock_consistency(self) -> None:
        """Warn if pyproject.toml is newer than uv.lock (indicating stale lock)."""
        start = time.perf_counter()
        pyproject = "pyproject.toml"
        lockfile = "uv.lock"

        if not os.path.exists(pyproject):
            self._add(CheckResult(
                name="Lockfile Consistency",
                passed=False,
                message="pyproject.toml not found.",
                duration_ms=(time.perf_counter() - start) * 1000,
            ))
            return

        if not os.path.exists(lockfile):
            self._add(CheckResult(
                name="Lockfile Consistency",
                passed=False,
                message="uv.lock not found.",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion="Run 'uv lock' to generate uv.lock from pyproject.toml.",
            ))
            return

        pyproject_mtime = os.path.getmtime(pyproject)
        lock_mtime = os.path.getmtime(lockfile)

        if pyproject_mtime > lock_mtime:
            self._add(CheckResult(
                name="Lockfile Consistency",
                passed=False,
                message="pyproject.toml is newer than uv.lock — lockfile is stale.",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion="Run 'uv lock' and commit the updated uv.lock before pushing.",
            ))
        else:
            self._add(CheckResult(
                name="Lockfile Consistency",
                passed=True,
                message="uv.lock is up-to-date with pyproject.toml.",
                duration_ms=(time.perf_counter() - start) * 1000,
            ))

    # ------------------------------------------------------------------
    # 10. GitHub Actions Workflow Schema (basic)
    # ------------------------------------------------------------------
    def check_workflow_yaml(self) -> None:
        """Perform basic structural validation on .github/workflows/*.yml files."""
        start = time.perf_counter()
        workflows_dir = ".github/workflows"
        if not os.path.isdir(workflows_dir):
            self._add(CheckResult(
                name="Workflow YAML Structure",
                passed=False,
                message=".github/workflows/ directory not found.",
                duration_ms=(time.perf_counter() - start) * 1000,
            ))
            return

        import yaml
        issues = []
        for fname in os.listdir(workflows_dir):
            if not fname.endswith((".yml", ".yaml")):
                continue
            fpath = os.path.join(workflows_dir, fname)
            try:
                with open(fpath, "r") as fh:
                    data = yaml.safe_load(fh)
            except yaml.YAMLError as exc:
                issues.append(f"{fname}: YAML parse error — {exc}")
                continue

            if not data or "jobs" not in data:
                issues.append(f"{fname}: missing 'jobs' key.")
                continue

            for job_name, job in data.get("jobs", {}).items():
                services = job.get("services", {})
                if "postgres" in services:
                    pg = services["postgres"]
                    if "options" not in pg or "health" not in str(pg.get("options", "")):
                        issues.append(
                            f"{fname} → job '{job_name}': postgres service missing healthcheck options."
                        )
                if "redis" in services:
                    rd = services["redis"]
                    if "options" not in rd or "health" not in str(rd.get("options", "")):
                        issues.append(
                            f"{fname} → job '{job_name}': redis service missing healthcheck options."
                        )

        passed = not issues
        self._add(CheckResult(
            name="Workflow YAML Structure",
            passed=passed,
            message="; ".join(issues) if issues else "Workflow files look healthy.",
            duration_ms=(time.perf_counter() - start) * 1000,
            suggestion="Add Docker healthcheck options to service containers." if issues else "",
        ))

    # ------------------------------------------------------------------
    # Run all checks
    # ------------------------------------------------------------------
    async def run_all(self) -> int:
        print("=" * 60)
        print("FastAPI CI/CD Pre-Flight Validation")
        print("=" * 60)
        print()

        # Sync checks
        self.check_env_vars()
        self.check_database_url()
        self.check_postgres_tcp()
        self.check_redis_tcp()
        self.check_alembic_config()
        self.check_pyproject_lock_consistency()
        self.check_workflow_yaml()

        # Async checks
        await self.check_postgres_auth()
        await self.check_redis_auth()
        await self.check_sqlalchemy_engine()

        # Summary
        print()
        print("=" * 60)
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        print(f"Results: {passed}/{total} passed, {failed} failed")
        print("=" * 60)

        if failed:
            print("\\n🔧 Next steps:")
            print("   1. Fix failed checks above.")
            print("   2. Re-run this script: python scripts/validate_ci_env.py")
            print("   3. Commit changes and push.")
            return 1
        else:
            print("\\n🚀 All checks passed! Safe to deploy.")
            return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate FastAPI CI/CD environment before deployment."
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug output")
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Connection timeout in seconds (default: 10)",
    )
    args = parser.parse_args()

    runner = ValidationRunner(verbose=args.verbose, timeout=args.timeout)
    return asyncio.run(runner.run_all())


if __name__ == "__main__":
    sys.exit(main())
'''

with open('/mnt/agents/output/validate_ci_env.py', 'w') as f:
    f.write(script_content)

print("Script saved to /mnt/agents/output/validate_ci_env.py")
print(f"Size: {len(script_content)} bytes")
