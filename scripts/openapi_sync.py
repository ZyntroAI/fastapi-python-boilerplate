#!/usr/bin/env python3
"""
OpenAPI Sync Script
Fetches OpenAPI spec from a running API server, validates it,
generates TypeScript/Python clients, and updates local files.

Usage:
    python scripts/openapi_sync.py --env dev
    python scripts/openapi_sync.py --url http://localhost:8000/openapi.json
    python scripts/openapi_sync.py --help
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
CONFIG = {
    "dev": {
        "spec_url": "http://localhost:8000/openapi.json",
        "spec_path": ROOT / "docs" / "openapi.json",
        "ts_output": ROOT.parent / "web" / "src" / "api" / "client.ts",
        "py_output": ROOT / "app" / "api_client.py",
    },
    "staging": {
        "spec_url": "https://staging-api.example.com/openapi.json",
        "spec_path": ROOT / "docs" / "openapi.staging.json",
        "ts_output": ROOT.parent / "web" / "src" / "api" / "client.staging.ts",
        "py_output": ROOT / "app" / "api_client_staging.py",
    },
    "prod": {
        "spec_url": "https://api.example.com/openapi.json",
        "spec_path": ROOT / "docs" / "openapi.json",
        "ts_output": ROOT.parent / "web" / "src" / "api" / "client.ts",
        "py_output": ROOT / "app" / "api_client.py",
    },
}

REQUIRED_TOOLS = {
    "ts": ("npx", "@openapi-generator-plus/openapi-generator-plus"),
    "py": ("pipx", "openapi-python-client"),
}


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def log(msg: str, level: str = "INFO") -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)


def check_tool(cmd: str, install_hint: str) -> bool:
    """Check if CLI tool is available"""
    try:
        subprocess.run(
            [cmd, "--version"],
            capture_output=True,
            check=False,
            timeout=10,
        )
        return True
    except FileNotFoundError:
        log(f"⚠️  {cmd} not found. Install with: {install_hint}", "WARN")
        return False


def fetch_spec(url: str) -> Dict[str, Any]:
    """Fetch and validate OpenAPI JSON spec"""
    log(f"📥 Fetching spec from: {url}")
    resp = httpx.get(url, timeout=30.0)
    resp.raise_for_status()
    spec: Dict[str, Any] = resp.json()
    
    # Basic validation
    if "openapi" not in spec and "swagger" not in spec:
        raise ValueError("Not a valid OpenAPI spec: missing openapi/swagger version")
    if "paths" not in spec:
        raise ValueError("Not a valid OpenAPI spec: missing paths")
    
    version = spec.get("openapi", spec.get("swagger", "unknown"))
    title = spec.get("info", {}).get("title", "API")
    log(f"✅ Valid spec: {title} (v{version}) — {len(spec.get('paths', {}))} endpoints")
    return spec


def save_spec(spec: Dict[str, Any], path: Path) -> None:
    """Save spec to JSON file with formatting"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    log(f"💾 Spec saved: {path}")


def generate_ts_client(spec_path: Path, output_path: Path) -> bool:
    """Generate TypeScript client using OpenAPI Generator Plus"""
    if not check_tool("npx", "npm install -g @openapi-generator-plus/openapi-generator-plus"):
        return False
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_dir = output_path.parent
    
    cmd = [
        "npx", "@openapi-generator-plus/openapi-generator-plus",
        "--input", str(spec_path),
        "--output-dir", str(output_dir),
        "--generator", "typescript-axios",
    ]
    
    try:
        log("🔧 Generating TypeScript client...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        log(f"✅ TypeScript client: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        log(f"❌ TypeScript generation failed:\n{e.stderr}", "ERROR")
        return False


def generate_py_client(spec_path: Path, output_path: Path) -> bool:
    """Generate Python client using openapi-python-client"""
    if not check_tool("openapi-python-client", "pipx install openapi-python-client"):
        return False
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            "openapi-python-client", "generate",
            "--path", str(spec_path),
            "--output", tmpdir,
            "--overwrite",
        ]
        
        try:
            log("🔧 Generating Python client...")
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Find the generated package and move it
            gen_dirs = [d for d in Path(tmpdir).iterdir() if d.is_dir() and not d.name.startswith(".")]
            if not gen_dirs:
                log("⚠️  Could not find generated Python package", "WARN")
                return False
            
            pkg_dir = gen_dirs[0]
            src_dir = pkg_dir / pkg_dir.name.replace("-", "_")
            
            if src_dir.exists():
                # Remove existing output
                if output_path.exists():
                    shutil.rmtree(output_path) if output_path.is_dir() else output_path.unlink()
                # Move entire package directory
                shutil.copytree(src_dir, output_path)
                log(f"✅ Python client: {output_path}")
            return True
        except subprocess.CalledProcessError as e:
            log(f"❌ Python generation failed:\n{e.stderr}", "ERROR")
            return False


def update_gitignore() -> None:
    """Ensure generated client paths are in .gitignore"""
    gitignore = ROOT / ".gitignore"
    entries = [
        "# Generated API clients",
        "/web/src/api/client.ts",
        "/app/api_client/",
    ]
    
    if not gitignore.exists():
        with open(gitignore, "w") as f:
            f.write("\n".join(entries) + "\n")
        return
    
    content = gitignore.read_text(encoding="utf-8")
    for entry in entries:
        if entry not in content:
            with open(gitignore, "a") as f:
                f.write(f"\n{entry}\n")
    log("📋 .gitignore updated")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Fetch OpenAPI spec and generate TypeScript/Python clients",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/openapi_sync.py --env dev
  python scripts/openapi_sync.py --url http://localhost:8000/openapi.json
  python scripts/openapi_sync.py --env prod --no-ts
        """,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--env", choices=list(CONFIG.keys()), help="Environment preset")
    group.add_argument("--url", help="Direct URL to OpenAPI JSON spec")
    
    parser.add_argument("--no-ts", action="store_true", help="Skip TypeScript client generation")
    parser.add_argument("--no-py", action="store_true", help="Skip Python client generation")
    parser.add_argument("--spec-path", help="Override path to save spec JSON")
    parser.add_argument("--dry-run", action="store_true", help="Fetch only, no generation")
    
    args = parser.parse_args()
    
    try:
        # Resolve config
        if args.url:
            spec_url = args.url
            spec_path = Path(args.spec_path) if args.spec_path else ROOT / "docs" / "openapi.json"
            ts_output = ROOT.parent / "web" / "src" / "api" / "client.ts"
            py_output = ROOT / "app" / "api_client"
        else:
            cfg = CONFIG[args.env]
            spec_url = cfg["spec_url"]
            spec_path = Path(args.spec_path) if args.spec_path else cfg["spec_path"]
            ts_output = cfg["ts_output"]
            py_output = cfg["py_output"]
        
        # Fetch and save spec
        spec = fetch_spec(spec_url)
        save_spec(spec, spec_path)
        
        if args.dry_run:
            log("🔍 Dry run complete — spec fetched, no clients generated")
            return
        
        # Generate clients
        results = {}
        if not args.no_ts:
            results["TypeScript"] = generate_ts_client(spec_path, ts_output)
        if not args.no_py:
            results["Python"] = generate_py_client(spec_path, py_output)
        
        # Summary
        log("\n📊 Summary:")
        log(f"  Spec: {spec_path}")
        for lang, ok in results.items():
            status = "✅" if ok else "❌"
            log(f"  {status} {lang} client")
        
        if all(results.values()):
            update_gitignore()
            log("\n🎉 All done! Clients are in sync ✅")
        else:
            sys.exit(1)
    
    except httpx.HTTPStatusError as e:
        log(f"❌ HTTP Error: {e.response.status_code} — {spec_url}", "ERROR")
        sys.exit(1)
    except Exception as e:
        log(f"❌ Error: {e}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
