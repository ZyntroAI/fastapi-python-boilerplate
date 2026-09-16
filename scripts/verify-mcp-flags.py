#!/usr/bin/env python3
"""Verify that every flag in an MCP server config is actually supported.

Why this exists
---------------
``chrome-devtools-mcp`` parses its CLI with a non-strict yargs schema: an
**unknown** flag is silently ignored and the process still starts normally.
A config with a typo'd or invented flag therefore looks healthy -- ``--help``
succeeds, the server boots, MCP clients connect -- while the security control
the flag was supposed to turn on is simply not applied.

That makes "the server started" worthless as a test. This script asserts the
opposite property: every flag named in the config appears in the server's own
``--help`` output for the pinned version.

Usage
-----
    python3 scripts/verify-mcp-flags.py docs/mcp/mcp-config.json
    python3 scripts/verify-mcp-flags.py docs/mcp/mcp-config.json --server chrome-devtools-mcp@1.9.0

Exit codes
----------
    0  every flag is supported
    1  one or more flags are unsupported (listed on stderr)
    2  the config could not be read or the server's --help could not be obtained
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

FLAG_RE = re.compile(r"--[A-Za-z][A-Za-z0-9-]*")


def normalise(flag: str) -> str:
    """``--redactNetworkHeaders`` / ``--redact-network-headers`` -> ``redactnetworkheaders``."""
    return flag.lstrip("-").replace("-", "").lower()


def load_config(path: Path) -> list[tuple[str, dict]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"error: config not found: {path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"error: config is not valid JSON: {path}: {exc}")

    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        sys.exit(f"error: no 'mcpServers' object in {path}")
    return [(str(k), v) for k, v in servers.items() if isinstance(v, dict)]


def help_text(package: str) -> str:
    cmd = ["npx", "-y", package, "--help"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        sys.exit("error: npx not found on PATH")
    except subprocess.TimeoutExpired:
        sys.exit(f"error: timed out running: {' '.join(cmd)}")

    out = (proc.stdout or "") + (proc.stderr or "")
    if not out.strip():
        sys.exit(f"error: no output from: {' '.join(cmd)}")
    return out


def supported_flags(help_output: str) -> set[str]:
    return {normalise(match) for match in FLAG_RE.findall(help_output)}


def is_supported(flag: str, supported: set[str]) -> bool:
    """A flag is supported if it, or the boolean it negates, is in --help.

    yargs accepts ``--no-<name>`` for any boolean declared as ``--name``, so
    ``--no-usage-statistics`` is valid whenever ``--usageStatistics`` is listed
    even though the negated spelling never appears in --help itself.
    """
    if normalise(flag) in supported:
        return True
    if flag.startswith("--no-"):
        return normalise(flag[5:]) in supported
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("config", type=Path, help="path to mcp-config.json")
    parser.add_argument(
        "--server",
        default=None,
        help="npm package spec to interrogate (default: inferred from the config, else chrome-devtools-mcp@latest)",
    )
    args = parser.parse_args()

    servers = load_config(args.config)

    # Work out which package to ask for --help. Prefer --server, else the pinned
    # spec found in the config's args, else latest.
    package = args.server
    if package is None:
        for _name, entry in servers:
            for token in entry.get("args", []):
                if isinstance(token, str) and token.startswith("chrome-devtools-mcp"):
                    package = token
                    break
            if package:
                break
    if package is None:
        package = "chrome-devtools-mcp@latest"

    print(f"config  : {args.config}")
    print(f"server  : {package}")
    help_output = help_text(package)
    supported = supported_flags(help_output)
    print(f"flags in --help: {len(supported)}\n")

    unsupported: list[tuple[str, str]] = []
    checked = 0

    for name, entry in servers:
        for token in entry.get("args", []):
            if not isinstance(token, str) or not token.startswith("--"):
                continue
            flag = token.split("=", 1)[0]
            checked += 1
            if is_supported(flag, supported):
                print(f"  ok    {flag}")
            else:
                print(f"  MISS  {flag}")
                unsupported.append((name, flag))

    print(f"\nchecked {checked} flag(s); {len(unsupported)} unsupported")

    if unsupported:
        print(
            "\nThese flags are NOT recognised by {} and will be silently ignored.\n"
            "Either remove them, or pass them through as Chrome arguments:\n"
            "  --chrome-arg='--flag-name'".format(package),
            file=sys.stderr,
        )
        for server_name, flag in unsupported:
            print(f"  [{server_name}] {flag}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
