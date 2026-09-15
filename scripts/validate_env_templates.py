#!/usr/bin/env python3
"""Validate every .env.example in this repo.

Checks, per template:
  * it parses as KEY=VALUE (or comment)
  * keys are well-formed and unique
  * no value looks like a real secret rather than a placeholder
  * every declared key is actually READ by the component it documents

And, repo-wide:
  * every variable the core app reads is documented in the root template

Run:
    python scripts/validate_env_templates.py

Exit codes:
    0 — all templates valid
    1 — one or more failures (warnings alone do not fail the run)
"""
from __future__ import annotations

import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# template -> the source directories that must prove they read its keys
TEMPLATES: dict[str, list[str]] = {
    ".env.example": ["app", "tests", "scripts", "providers", "docker", "k8s",
                     "backend", "services", "api", "lib", "middleware", "cache.py"],
    "graphql_api/.env.example": ["graphql_api"],
    "frontend/.env.example": ["frontend"],
    "scripts/.env.example": ["scripts"],
    "deliverables/pm-backend/.env.example": ["deliverables/pm-backend"],
    "deliverables/fastapi-obsidian-backend/.env.example": ["deliverables/fastapi-obsidian-backend"],
    "deliverables/agent-security-suite/.env.example": ["deliverables/agent-security-suite"],
    "deliverables/manus-client/.env.example": ["deliverables/manus-client"],
    "deliverables/product-crud/server/.env.example": ["deliverables/product-crud/server"],
    "deliverables/product-crud/web/.env.example": ["deliverables/product-crud/web"],
    "deliverables/agent-core/.env.example": ["deliverables/agent-core"],
}

READ_PAT = re.compile(
    r"""(?:os\.getenv|os\.environ\.get|os\.environ\[)\s*\(?\s*['"]([A-Z][A-Z0-9_]{2,})['"]"""
    r"""|process\.env\.([A-Z][A-Z0-9_]{2,})"""
    r"""|import\.meta\.env\.([A-Z][A-Z0-9_]{2,})"""
    r"""|\$\{\{\s*secrets\.([A-Za-z0-9_]+)\s*\}\}"""
    r"""|\$\{([A-Z][A-Z0-9_]{2,})\]"""
    r"""|\$\{([A-Z][A-Z0-9_]{2,}):-"""
    r"""|env\(\s*['"]([A-Z][A-Z0-9_]{2,})['"]\s*\)"""
)

YAML_KEY = re.compile(r"^\s{2,}([A-Z][A-Z0-9_]{2,})\s*[:=]")
# pydantic-settings / dataclass field declaration: `NAME: str = ...`
DECL_FIELD = re.compile(
    r"^\s{0,4}([A-Z][A-Z0-9_]{2,})\s*:\s*(?:str|int|bool|float|list|Optional|Annotated)"
)

# Keys that legitimately appear in a template without a matching source read:
# values injected by YAML/compose, consumed by a dependency we do not scan, or
# explicitly marked "Reserved" in the template as not-yet-consumed.
KNOWN_OK = {
    "DB_PASSWORD", "MINIO_PASSWORD", "GRAFANA_PASSWORD",
    "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB",
    "POSTGRES_INITDB_ARGS", "DEFAULT_TZ", "TZ",
    "OBSIDIAN_API_TOKEN", "OBSIDIAN_VERIFY_SSL",
    "JWT_ALGORITHM", "JWT_EXPIRE_MINUTES",
    "OAUTH_CLIENT_SECRET", "OAUTH_AUTHORIZE_URL", "OAUTH_TOKEN_URL",
    "OAUTH_USERINFO_URL", "DEBUG", "PORT", "APP_VERSION",
    "JWT_TTL_MINUTES", "ENCRYPTION_KEY", "ENCRYPT_AT_REST",
    "TOOL_STATE_FILE", "BILLING_BASE_URL", "VITE_API_PROXY",
    "MANUS_BEARER_TOKEN", "NODE_ENV", "CORS_ORIGIN", "VITE_API_BASE_URL",
    "SKILLS_DIR", "DATA_DIR", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES",
    "REDIS_SUB_CHANNEL", "SECRET_KEY", "REDIS_PASSWORD",
    "APP_NAME", "ENV", "LOG_LEVEL", "API_BASE_URL",
    "ENCRYPTION_SECRET", "PADDLE_SANDBOX_BASE_URL",
    # Marked "Reserved" in the template: planned infra, no code reads them yet.
    "VAULT_ADDR", "VAULT_ROLE", "ALERT_SLACK_WEBHOOK",
}

SECRETISH = re.compile(
    r"(?:sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|"
    r"-----BEGIN [A-Z ]+PRIVATE KEY-----|xox[baprs]-[A-Za-z0-9-]{10,})"
)

SCAN_EXT = (".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
            ".yml", ".yaml", ".prisma", ".json")
SKIP_DIRS = {"node_modules", "__pycache__", ".venv", "venv", "dist", ".next",
             ".git", "coverage", ".turbo"}


def collect(dirs: list[str]) -> set[str]:
    """Every env var name the given paths read."""
    found: set[str] = set()
    for d in dirs:
        base = ROOT / d
        if not base.exists():
            continue
        if base.is_file():
            walk = [(base.parent, [base.name])]
        else:
            walk = []
            for dp, dn, fn in os.walk(base):
                dn[:] = [x for x in dn if x not in SKIP_DIRS]
                walk.append((dp, fn))
        for dp, files in walk:
            for fn in files:
                if not fn.endswith(SCAN_EXT):
                    continue
                try:
                    text = (pathlib.Path(dp) / fn).read_text(
                        encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for m in READ_PAT.finditer(text):
                    v = next((g for g in m.groups() if g), None)
                    if v:
                        found.add(v)
                for line in text.splitlines():
                    md = DECL_FIELD.match(line)
                    if md:
                        found.add(md.group(1))
                if fn.endswith((".yml", ".yaml")):
                    for line in text.splitlines():
                        mk = YAML_KEY.match(line)
                        if mk:
                            found.add(mk.group(1))
    return found


def declared(path: pathlib.Path) -> tuple[list[str], list[str]]:
    """Parse a template into (keys, problems)."""
    keys: list[str] = []
    problems: list[str] = []
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            problems.append(f"line {i}: not a KEY=VALUE or comment")
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip()
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
            problems.append(f"line {i}: malformed key {key!r}")
            continue
        keys.append(key)
        if SECRETISH.search(val):
            problems.append(f"line {i}: {key} looks like a REAL secret")
    dupes = {k for k in keys if keys.count(k) > 1}
    if dupes:
        problems.append(f"duplicate keys: {sorted(dupes)}")
    return keys, problems


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []

    print("=" * 76)
    print("TEMPLATE VALIDATION")
    print("=" * 76)
    for rel, dirs in TEMPLATES.items():
        p = ROOT / rel
        if not p.exists():
            failures.append(f"MISSING template: {rel}")
            print(f"\nFAIL  {rel}  (missing)")
            continue
        keys, problems = declared(p)
        read = collect(dirs)
        unresolved = [k for k in keys if k not in read and k not in KNOWN_OK]
        ok = not problems and not unresolved
        print(f"\n{'PASS' if ok else 'CHECK'}  {rel}  ({len(keys)} vars)")
        for pb in problems:
            print(f"      x {pb}")
            failures.append(f"{rel}: {pb}")
        if unresolved:
            print(f"      ! not found in code reads: {', '.join(sorted(unresolved))}")
            warnings.append(f"{rel}: unresolved {sorted(unresolved)}")

    print()
    print("=" * 76)
    print("COVERAGE — core app vars vs root template")
    print("=" * 76)
    root_keys = set(declared(ROOT / ".env.example")[0])
    app_read = collect(["app"])
    missing = sorted(app_read - root_keys)
    if missing:
        print(f"app/ reads but root template omits: {missing}")
        warnings.append(f"app vars missing from root template: {missing}")
    else:
        print(f"all {len(app_read)} vars read by app/ are documented: OK")

    print()
    print("=" * 76)
    print(f"RESULT: {len(failures)} failures, {len(warnings)} warnings")
    print("=" * 76)
    for f in failures:
        print(f"  FAIL  {f}")
    for w in warnings:
        print(f"  warn  {w}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
