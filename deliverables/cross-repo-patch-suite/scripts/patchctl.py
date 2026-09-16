#!/usr/bin/env python3
"""patchctl — command line for the cross-repo patch suite.

Dry-run is the default on every mutating command; ``--apply`` is required to
actually write. This is deliberate: an append that rewrites a file's line
endings looks fine until the diff is reviewed.

Usage::

    patchctl append   FILE --text "..." [--no-align] [--apply]
    patchctl verify   FILE --before-sha SHA256   # after an append
    patchctl guard    PATH --intent replace [--approval PATH]
    patchctl eol      ROOT [--patterns '*.yml']
    patchctl yaml     FILE
    patchctl pins     ROOT [--resolve]
    patchctl check    PATCH --in REPO
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from patchsuite import (  # noqa: E402
    Intent,
    append_text,
    audit_pins,
    diff_stat,
    guard,
    resolve_sha,
    safe_read,
    validate_yaml_file,
    verify_append,
)
from patchsuite import eol as eolmod  # noqa: E402
from patchsuite import gitops  # noqa: E402


def _emit(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    for key, value in payload.items():
        print(f"{key}: {value}")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def cmd_append(args: argparse.Namespace) -> int:
    target = Path(args.file)
    before = safe_read(target)
    result = append_text(target, args.text, align=not args.no_align, dry_run=not args.apply)
    payload = result.as_dict()
    payload["existing_sha256"] = hashlib.sha256(before).hexdigest()
    payload["diff"] = diff_stat(before, safe_read(target) if args.apply else before + b"")
    payload["mode"] = "applied" if args.apply else "dry-run (pass --apply to write)"
    _emit(payload, args.json)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    target = Path(args.file)
    after = safe_read(target)
    if args.before_sha:
        before = Path(args.before_file).read_bytes() if args.before_file else b""
        if not args.before_file:
            print(
                "verify needs --before-file (a copy of the file before the append) "
                "to compare against; the stored hash alone cannot reconstruct bytes.",
                file=sys.stderr,
            )
            return 2
    else:
        print("verify requires --before-file", file=sys.stderr)
        return 2
    verification = verify_append(before, after)
    _emit(verification.as_dict(), args.json)
    return 0 if verification.ok else 1


def cmd_guard(args: argparse.Namespace) -> int:
    result = guard(args.path, args.intent, approval=args.approval)
    _emit(result.as_dict(), args.json)
    return 0 if result.allowed else 1


def cmd_eol(args: argparse.Namespace) -> int:
    patterns = tuple(args.patterns.split(",")) if args.patterns else ("*.yml", "*.yaml")
    risks = gitops.audit_eol_risk(args.root, patterns=patterns)
    flagged = [r for r in risks if r.at_risk]
    payload = {
        "scanned": len(risks),
        "at_risk": len(flagged),
        "files": [r.as_dict() for r in risks],
    }
    _emit(payload, args.json)
    return 1 if flagged else 0


def cmd_yaml(args: argparse.Namespace) -> int:
    check = validate_yaml_file(args.file)
    _emit(check.as_dict(), args.json)
    return 0 if check.valid else 1


def cmd_pins(args: argparse.Namespace) -> int:
    audit = audit_pins(args.root, patterns=tuple(args.patterns.split(",")) if args.patterns else ("*.yml", "*.yaml"))
    payload = audit.as_dict()
    if args.resolve:
        resolutions = []
        for ref in audit.unpinned:
            sha = resolve_sha(ref.action, ref.ref)
            resolutions.append({"raw": ref.raw, "resolved_sha": sha, "file": ref.file, "line": ref.line})
        payload["resolutions"] = resolutions
    _emit(payload, args.json)
    return 0 if audit.compliant else 1


def cmd_check(args: argparse.Namespace) -> int:
    diag = gitops.check_patch(Path(args.patch), args.repo)
    _emit(diag.as_dict(), args.json)
    return 0 if diag.applies else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="patchctl", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("append", help="append text, preserving existing line endings")
    p.add_argument("file")
    p.add_argument("--text", required=True)
    p.add_argument("--no-align", action="store_true", help="do not rewrite payload endings to match the file")
    p.add_argument("--apply", action="store_true", help="actually write (default is dry-run)")
    p.set_defaults(func=cmd_append)

    p = sub.add_parser("verify", help="prove an append changed only appended bytes")
    p.add_argument("file")
    p.add_argument("--before-file", required=True)
    p.add_argument("--before-sha")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("guard", help="decide whether a write may proceed")
    p.add_argument("path")
    p.add_argument("--intent", choices=[i.value for i in Intent], required=True)
    p.add_argument("--approval")
    p.set_defaults(func=cmd_guard)

    p = sub.add_parser("eol", help="audit files for CRLF-without-trailing-newline risk")
    p.add_argument("root")
    p.add_argument("--patterns", help="comma-separated globs, e.g. '*.yml,*.yaml'")
    p.set_defaults(func=cmd_eol)

    p = sub.add_parser("yaml", help="validate a YAML file and locate the fault")
    p.add_argument("file")
    p.set_defaults(func=cmd_yaml)

    p = sub.add_parser("pins", help="audit and optionally resolve action references")
    p.add_argument("root")
    p.add_argument("--patterns")
    p.add_argument("--resolve", action="store_true")
    p.set_defaults(func=cmd_pins)

    p = sub.add_parser("check", help="check a patch applies, with a diagnosis")
    p.add_argument("patch")
    p.add_argument("--in", dest="repo", required=True)
    p.set_defaults(func=cmd_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
