"""Command line entry point — ``python -m cache_reduction <command>``.

Commands
--------
scan      Audit a file or directory for cache smells (CR1xx / CR2xx)
headers   Analyse a response's Cache-Control, optionally against its new build
redis     Audit pasted Redis INFO output

Every command prints JSON with ``--json`` and a human summary otherwise.
Exit code is 1 when any finding is high severity, so it drops straight into CI.
"""

from __future__ import annotations

import argparse
import json
import sys

from .cache_audit import SKIP_DIRS, scan_path
from .headers import analyze_cache_headers
from .redis_audit import audit_redis_info, audit_redis_infos


def _die(message: str, code: int = 2) -> int:
    print(message, file=sys.stderr)
    return code


def _cmd_scan(args: argparse.Namespace) -> int:
    # --skip adds to the built-in excludes; it never replaces them, so vendor
    # and build directories stay out of the scan by default.
    skip = set(SKIP_DIRS) | (set(args.skip) if args.skip else set())
    report = scan_path(args.path, extensions=args.ext, skip_dirs=skip)
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.summary())
        for f in report.findings:
            print(f"  [{f.severity.upper()}] {f.code} {f.path}:{f.line} — {f.message}")
    return 1 if report.by_severity()["high"] else 0


def _cmd_headers(args: argparse.Namespace) -> int:
    before = args.before
    after = args.after
    if before is None:
        before = _read(sys.stdin) if not sys.stdin.isatty() else ""
    result = analyze_cache_headers(before, after)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        state = "cacheable" if result["cacheable"] else "not cacheable"
        print(f"{state} — {result['cacheable_reason']}")
        print(f"  directives: {result['directives'] or '(none)'}")
        if "stale_after_change" in result:
            print(f"  stale after this change: {result['stale_after_change']}")
        if not result["findings"]:
            print("  no header issues")
        for f in result["findings"]:
            print(f"  [{f['severity'].upper()}] {f['code']} — {f['message']}")
    highs = [f for f in result["findings"] if f["severity"] == "high"]
    return 1 if highs else 0


def _read(stream) -> str:
    return stream.read()


def _cmd_redis(args: argparse.Namespace) -> int:
    if args.file:
        text = open(args.file, encoding="utf-8", errors="ignore").read()
    else:
        text = _read(sys.stdin)
    result = audit_redis_info(text, name=args.name, fail_open=not args.fail_closed)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['name']}: {result['used_memory_human']} used / "
              f"{result['maxmemory_human']} max, policy {result['maxmemory_policy']}")
        if result["hit_rate"] is not None:
            print(f"  hit rate {result['hit_rate']:.1%}  "
                  f"({int(result['keyspace_hits']):,} hits / "
                  f"{int(result['keyspace_misses']):,} misses)")
        if result["ttl_coverage"] is not None:
            print(f"  {result['ttl_coverage']:.1%} of {result['total_keys']:,} keys "
                  f"carry a TTL — up to {result['reclaimable_human']} reclaimable")
        print(f"  {result['key_safety']}")
        for f in result["findings"]:
            print(f"  [{f['severity'].upper()}] {f['code']} — {f['message']}")
    highs = [f for f in result["findings"] if f["severity"] == "high"]
    return 1 if highs else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cache_reduction", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="audit a file or directory for cache smells")
    p_scan.add_argument("path")
    p_scan.add_argument("--ext", nargs="*", default=None,
                        help="file extensions to include (default: Python/TS/JS/MD/YAML)")
    p_scan.add_argument("--skip", nargs="*", default=None,
                        help="extra directory names to exclude, e.g. --skip tests")
    p_scan.add_argument("--json", action="store_true")
    p_scan.set_defaults(func=_cmd_scan)

    p_hdr = sub.add_parser("headers", help="analyse Cache-Control on a response")
    p_hdr.add_argument("--before", help="raw header block of the current response")
    p_hdr.add_argument("--after", help="raw header block of the new build")
    p_hdr.add_argument("--json", action="store_true")
    p_hdr.set_defaults(func=_cmd_headers)

    p_redis = sub.add_parser("redis", help="audit Redis INFO output")
    p_redis.add_argument("--file", help="path to a saved INFO dump (default: stdin)")
    p_redis.add_argument("--name", default="default")
    p_redis.add_argument("--fail-closed", action="store_true",
                         help="the service treats a Redis outage as a hard failure")
    p_redis.add_argument("--json", action="store_true")
    p_redis.set_defaults(func=_cmd_redis)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
