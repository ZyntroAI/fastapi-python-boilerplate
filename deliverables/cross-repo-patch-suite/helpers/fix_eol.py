#!/usr/bin/env python3
"""Helper — repair the file state that makes `git am` fail.

Finds files whose line endings will break ``git am`` (CRLF with no trailing
newline) and gives them the one of two safe shapes:

* ``--to lf``   — normalise to LF (the repo's ``.gitattributes`` target)
* ``--to crlf`` — keep CRLF, but close the missing final newline

Either way the change is reported as a diff stat first, so you can see that the
repair touches only the line it must.

    python helpers/fix_eol.py .github/workflows --to crlf
    python helpers/fix_eol.py .github/workflows --to lf --apply
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from patchsuite import audit_eol_risk, diff_stat, normalize_terminators  # noqa: E402
from patchsuite import eol as eolmod  # noqa: E402


def repair_bytes(raw: bytes, to: str) -> bytes:
    """Return a safely-shaped version of ``raw``.

    ``lf`` normalises endings; ``crlf`` keeps the file's endings and only closes
    an unterminated final line. Neither inserts or removes content.
    """
    terminator = b"\r\n" if to == "crlf" else b"\n"
    out = normalize_terminators(raw, terminator)
    if not out.endswith(terminator):
        out += terminator
    return out


def run(root: Path, to: str, *, apply: bool = False, patterns: tuple[str, ...] = ("*.yml", "*.yaml")):
    risks = audit_eol_risk(root, patterns=patterns)
    repairs = []
    for risk in risks:
        if not risk.at_risk:
            continue
        path = root / risk.path
        before = path.read_bytes()
        after = repair_bytes(before, to)
        stat = diff_stat(before, after)
        if apply:
            path.write_bytes(after)
        repairs.append(
            {
                "path": risk.path,
                "from": risk.eol,
                "to": to,
                "final_newline_before": risk.final_newline,
                "final_newline_after": eolmod.ends_with_newline(after),
                "diff": stat,
            }
        )
    return {"scanned": len(risks), "repaired": len(repairs), "files": repairs, "applied": apply}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root")
    parser.add_argument("--to", choices=["lf", "crlf"], default="lf")
    parser.add_argument("--patterns", help="comma-separated globs")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    patterns = tuple(args.patterns.split(",")) if args.patterns else ("*.yml", "*.yaml")
    report = run(Path(args.root), args.to, apply=args.apply, patterns=patterns)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"scanned: {report['scanned']}  at-risk: {report['repaired']}")
        for item in report["files"]:
            print(f"  {item['path']}  {item['from']} -> {item['to']}  diff={item['diff']}")
        if not args.apply and report["repaired"]:
            print("\nDry run — re-run with --apply to repair.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
