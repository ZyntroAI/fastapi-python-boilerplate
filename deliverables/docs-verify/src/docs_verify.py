"""docs_verify — check that repository documentation still describes the repository.

The README, `PROBLEMS.md` and `LICENSE` make claims a reader takes on trust:
counts, paths, workflow names, licence holder. Those claims go stale silently
when the tree moves underneath them — a merge adds a deliverable and the README
keeps saying 24, or a count is hand-fixed and drifts again a week later.

This module turns as many of those claims as it can into assertions against the
real tree, so drift fails loudly instead of quietly.

Design rules:

* **Compare, don't hard-code.** A count in the README is checked against the
  tree and against the number the README itself declares, so the check survives
  the tree legitimately changing. Only facts that cannot move (a section must
  exist, a licence holder must not be a placeholder) are asserted absolutely.
* **Read-only.** Nothing here writes. No network.
* **Pure standard library.** PyYAML is used when present; a missing-PyYAML
  environment reports those checks as skipped rather than failing.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

__all__ = ["Check", "Report", "verify", "render", "PASS", "FAIL", "SKIP"]

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"


@dataclass
class Check:
    name: str
    status: str
    detail: str = ""


@dataclass
class Report:
    checks: list[Check] = field(default_factory=list)

    def add(self, name: str, ok: bool | None, detail: str = "") -> None:
        status = SKIP if ok is None else (PASS if ok else FAIL)
        self.checks.append(Check(name, status, detail))

    @property
    def failures(self) -> list[Check]:
        return [c for c in self.checks if c.status == FAIL]

    @property
    def skipped(self) -> list[Check]:
        return [c for c in self.checks if c.status == SKIP]

    @property
    def passed(self) -> bool:
        return not self.failures


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


# --------------------------------------------------------------------------
# individual checks
# --------------------------------------------------------------------------

def _check_counts(root: Path, readme: str, r: Report) -> None:
    """Counts the README declares, compared against the tree."""
    m = re.search(r"holds (\d+) self-contained", readme)
    if m:
        declared = int(m.group(1))
        actual = len([p for p in (root / "deliverables").glob("*") if p.is_dir()])
        r.add("README deliverables count matches tree", declared == actual,
              f"declared={declared} tree={actual}")
    else:
        r.add("README declares a deliverables count", False,
              "no 'holds N self-contained' phrase found")

    m = re.search(r"Reference library \((\d+) files\)", readme)
    if m:
        declared = int(m.group(1))
        docs = root / "docs"
        actual = len([p for p in docs.rglob("*") if p.is_file()]) if docs.is_dir() else 0
        r.add("README docs count matches tree", declared == actual,
              f"declared={declared} tree={actual}")
    else:
        r.add("README declares a docs count", None, "no 'Reference library (N files)' phrase")

    m = re.search(r"(\d+)\s+workflow files", readme, re.I) \
        or re.search(r"of the\s+(\w+)\s+workflow files", readme, re.I)
    wf = root / ".github" / "workflows"
    if wf.is_dir():
        actual = len([p for p in wf.iterdir() if p.is_file()])
        if m:
            raw = m.group(1)
            words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                     "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
                     "twelve": 12}
            declared = int(raw) if raw.isdigit() else words.get(raw.lower())
            if declared is None:
                r.add("README workflow count matches tree", None, f"unparsed={raw!r}")
            else:
                r.add("README workflow count matches tree", declared == actual,
                      f"declared={declared} tree={actual}")
        else:
            r.add("README declares a workflow count", None, f"tree={actual}")


def _check_every_deliverable_listed(root: Path, readme: str, r: Report) -> None:
    """Each deliverables/ entry should be named somewhere in the README."""
    d = root / "deliverables"
    if not d.is_dir():
        r.add("deliverables/ exists", False)
        return
    named = set(re.findall(r"`([a-z0-9][a-z0-9-]+)`", readme))
    tree = {p.name for p in d.iterdir() if p.is_dir()}
    missing = sorted(tree - named)
    r.add("README names every deliverable", not missing,
          f"missing={missing}" if missing else f"{len(tree)} listed")


def _check_paths_exist(root: Path, readme: str, r: Report) -> None:
    """Backticked paths the README presents as present must resolve.

    Only plain `dir/file` shapes are considered. A candidate is skipped when it
    looks like a filename pattern rather than a path — a `.` joined token
    (`a.yaml/.json`), a glob, or a build artefact name — because those name
    files inside a directory that may not exist yet.
    """
    cands = set(re.findall(r"`([a-z0-9_-]+/[a-z0-9_./-]+)`", readme))
    claims = []
    for c in sorted(cands):
        if c.startswith(("http", "docs/releases")):
            continue
        if "/." in c or "*" in c or c.count("/") > 2:
            continue
        seg = c.split("/", 1)[1]
        if "." in seg and seg.split(".")[-1] in {"yaml", "json", "md", "txt", "yml"} \
                and "/" in seg:
            # a deep filename pattern, not a directory claim
            continue
        claims.append(c)
    broken = [c for c in claims if not (root / c).exists()]
    r.add("README paths resolve", not broken,
          f"broken={broken[:8]}" if broken else f"{len(claims)} checked")


def _check_license(root: Path, r: Report) -> None:
    lic = _read(root / "LICENSE")
    if lic is None:
        r.add("LICENSE present", False)
        return
    r.add("LICENSE has no placeholder brackets", "[" not in lic.split("\n")[2],
          lic.split("\n")[2] if lic.count("\n") >= 2 else "")
    holder = re.search(r"Copyright \(c\) \d{4} (.+)$", lic, re.M)
    r.add("LICENSE names a holder", bool(holder and holder.group(1).strip()),
          holder.group(1).strip() if holder else "no Copyright line")


def _check_package_license(root: Path, r: Report) -> None:
    p = root / "package.json"
    if not p.exists():
        r.add("package.json present", None, "not found")
        return
    try:
        d = json.loads(_read(p) or "{}")
    except json.JSONDecodeError as e:
        r.add("package.json parses", False, str(e))
        return
    r.add("package.json parses", True)
    r.add("package.json declares a license", bool(d.get("license")),
          repr(d.get("license")))


def _check_workflows(root: Path, r: Report) -> None:
    wf = root / ".github" / "workflows"
    if not wf.is_dir():
        r.add("workflows directory present", False)
        return
    files = sorted(p for p in wf.iterdir() if p.is_file())
    try:
        import yaml  # type: ignore
    except ImportError:
        r.add("workflows parse as YAML", None, "PyYAML unavailable — skipped")
        return

    broken = []
    for p in files:
        try:
            list(yaml.safe_load_all(_read(p) or ""))
        except Exception as e:  # noqa: BLE001 - report any parse failure
            broken.append(f"{p.name}: {str(e).splitlines()[0][:60]}")
    r.add("workflows parse as YAML", not broken,
          f"{len(files) - len(broken)}/{len(files)} ok; broken={broken}" if broken
          else f"{len(files)} ok")


def _check_action_pins(root: Path, r: Report) -> None:
    """Report the SHA-pin split. Not a pass/fail policy — a measurement."""
    wf = root / ".github" / "workflows"
    if not wf.is_dir():
        return
    total = pinned = 0
    for p in sorted(wf.iterdir()):
        if not p.is_file():
            continue
        for m in re.finditer(r"uses:\s*([^\s#]+)", _read(p) or ""):
            ref = m.group(1)
            if "@" not in ref:
                continue
            total += 1
            if re.fullmatch(r"[0-9a-f]{40}", ref.split("@", 1)[1]):
                pinned += 1
    if total:
        r.add("action pin count measured", True,
              f"{pinned}/{total} pinned, {total - pinned} unpinned")


def _check_problems(root: Path, r: Report) -> None:
    p = root / "PROBLEMS.md"
    if not p.exists():
        r.add("PROBLEMS.md present", None, "not found")
        return
    t = _read(p) or ""

    # A real entry heading is `### P-00N — title`. Requiring the em dash after the
    # id excludes meta headings that name two ids at once
    # (`### P-001 / P-002 — re-verified today`), which are not duplicate entries.
    ids = re.findall(r"^### (P-\d{3})\s+\u2014", t, re.M)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    r.add("problem ids unique", not dupes, f"duplicated={dupes}" if dupes else f"{len(ids)} entries")

    dates = re.findall(r"^## \[(\d{4}-\d{2}-\d{2})\]", t, re.M)
    dup_dates = sorted({d for d in dates if dates.count(d) > 1})
    r.add("date sections unique", not dup_dates,
          f"duplicated={dup_dates}" if dup_dates else f"{len(dates)} sections")
    r.add("date sections newest-first", dates == sorted(dates, reverse=True),
          "out of order" if dates != sorted(dates, reverse=True) else "")


def _check_readme_sections(root: Path, r: Report) -> None:
    t = _read(root / "README.md") or ""
    required = ["## License", "## Tests", "## Deliverables"]
    missing = [s for s in required if s not in t]
    r.add("README keeps core sections", not missing,
          f"missing={missing}" if missing else f"{len(required)} present")


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def verify(root: str | os.PathLike[str] = ".") -> Report:
    """Run every check against ``root`` and return the report."""
    root = Path(root).resolve()
    r = Report()

    readme = _read(root / "README.md")
    r.add("README.md present", readme is not None)
    if readme is None:
        return r

    r.add("README carries no fabricated draft heading",
          "Origin Branch Strategy" not in readme)

    _check_counts(root, readme, r)
    _check_every_deliverable_listed(root, readme, r)
    _check_paths_exist(root, readme, r)
    _check_readme_sections(root, r)
    _check_license(root, r)
    _check_package_license(root, r)
    _check_workflows(root, r)
    _check_action_pins(root, r)
    _check_problems(root, r)
    return r


def render(r: Report) -> str:
    lines = []
    for c in r.checks:
        mark = {PASS: "ok  ", FAIL: "FAIL", SKIP: "skip"}[c.status]
        pad = "" if not c.detail else f"  ({c.detail})"
        lines.append(f"  {mark} {c.name}{pad}")
    n = len(r.checks)
    lines.append("")
    lines.append(f"{n - len(r.failures) - len(r.skipped)}/{n} passed, "
                 f"{len(r.failures)} failed, {len(r.skipped)} skipped")
    return "\n".join(lines)
