"""Static cache-footprint audit.

Scans source text (never a live cache) and reports the cache mistakes that
actually cost memory in production:

  CR1xx  app-layer cache   — keys with no TTL, sentinel TTLs, unbounded
                             memoization, wildcard deletes, full flushes
  CR2xx  agent context     — oversized prompt files, repeated blocks,
                             inlined external URLs

Deterministic by construction: same input text, same findings, same order.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

DEFAULT_EXTENSIONS: tuple[str, ...] = (
    ".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".md", ".yml", ".yaml", ".json", ".toml",
)

SKIP_DIRS: frozenset[str] = frozenset({
    ".git", "node_modules", ".venv", "venv", "__pycache__", "dist",
    "build", ".next", ".turbo", "coverage", ".pytest_cache", ".mypy_cache",
})

#: Weight of one finding at each severity — lower score is better.
SEVERITY_WEIGHT: dict[str, int] = {"high": 5, "medium": 2, "low": 1}

#: TTL values that look like a timeout but never expire anything.
SENTINEL_TTLS: frozenset[int] = frozenset({0, -1, 99999999, 1000000000})

#: Character budget for a single agent-context file before it is flagged.
PROMPT_CHAR_BUDGET = 30_000

#: Minimum size for a blank-line-separated block to count as a repeatable unit.
BLOCK_MIN_CHARS = 200

_CACHE_WRITE = re.compile(
    r"\b(?:await\s+)?(?:cache|redis|r|client)\s*\.\s*set(?:ex|nx|exnx)?\s*\(",
    re.I,
)
_CACHE_DECORATOR = re.compile(
    r"@(?:cache|cached|lru_cache|ttl_cache|redis_cache|memoize)\b",
    re.I,
)
_TTL_KEY = re.compile(r"\b(?:ttl|ex|expire|expires|expiration)\s*[:=]\s*(-?\d+)", re.I)
_MAXSIZE_KEY = re.compile(r"\bmaxsize\s*=", re.I)
_SETEX_NUMERIC = re.compile(r"\bsetex\s*\(\s*[^,]+,\s*(-?\d+)\s*,", re.I)
_FLUSH_ALL = re.compile(r"\b(?:flushdb|flushall)\s*\(", re.I)
_WILDCARD_DELETE = re.compile(r"\.keys\s*\(\s*['\"]([^'\"]*\*[^'\"]*)['\"]\s*\)", re.I)
_EXTERNAL_URL = re.compile(r"https?://\S+")


@dataclass(frozen=True)
class Finding:
    """One cache smell, anchored to a file and line."""

    code: str
    severity: str
    path: str
    line: int
    message: str
    evidence: str = ""

    @property
    def weight(self) -> int:
        return SEVERITY_WEIGHT.get(self.severity, 0)

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "severity": self.severity,
            "path": self.path,
            "line": self.line,
            "message": self.message,
            "evidence": self.evidence,
        }


@dataclass
class AuditReport:
    """Findings for one scan, with a graded score."""

    root: str = ""
    files_scanned: int = 0
    findings: list[Finding] = field(default_factory=list)

    @property
    def score(self) -> int:
        """Weighted penalty — 0 is a clean scan. Lower is better."""
        return sum(f.weight for f in self.findings)

    @property
    def grade(self) -> str:
        s = self.score
        if s == 0:
            return "A"
        if s <= 3:
            return "B"
        if s <= 9:
            return "C"
        if s <= 19:
            return "D"
        return "F"

    def by_severity(self) -> dict[str, int]:
        counts = {"high": 0, "medium": 0, "low": 0}
        for f in self.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts

    def codes(self) -> list[str]:
        return sorted({f.code for f in self.findings})

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "files_scanned": self.files_scanned,
            "score": self.score,
            "grade": self.grade,
            "by_severity": self.by_severity(),
            "codes": self.codes(),
            "findings": [f.to_dict() for f in self.findings],
        }

    def summary(self) -> str:
        sev = self.by_severity()
        if not self.findings:
            return (
                f"Scanned {self.files_scanned} file(s) — no cache issues found "
                f"(grade A)."
            )
        return (
            f"Scanned {self.files_scanned} file(s) — {len(self.findings)} finding(s) "
            f"(grade {self.grade}, score {self.score}): "
            f"{sev['high']} high, {sev['medium']} medium, {sev['low']} low."
        )


def _window(lines: Sequence[str], index: int, span: int = 5) -> str:
    return "\n".join(lines[index:index + span])


def scan_text(text: str, path: str = "<text>") -> list[Finding]:
    """Return every cache finding in ``text``, in line order."""
    findings: list[Finding] = []
    lines = text.splitlines()
    is_prompt = path.endswith(".md")
    is_app = not is_prompt

    if is_app:
        for i, line in enumerate(lines):
            window = _window(lines, i)

            # setex carries its TTL as a positional argument, so it must be
            # checked before the generic "cache write" rule below — otherwise
            # every setex looks like a write with no TTL.
            setex = _SETEX_NUMERIC.search(line)
            if setex:
                if int(setex.group(1)) in SENTINEL_TTLS:
                    findings.append(Finding(
                        "CR102", "medium", path, i + 1,
                        f"Sentinel TTL ({setex.group(1)}) on setex does not "
                        "expire the key.",
                        line.strip()[:160],
                    ))
                continue

            if _CACHE_WRITE.search(line):
                if not _TTL_KEY.search(window):
                    findings.append(Finding(
                        "CR101", "high", path, i + 1,
                        "Cache write with no TTL in the surrounding block — "
                        "the key lives until it is evicted or memory runs out.",
                        line.strip()[:160],
                    ))
                else:
                    m = _TTL_KEY.search(window)
                    if m and int(m.group(1)) in SENTINEL_TTLS:
                        findings.append(Finding(
                            "CR102", "medium", path, i + 1,
                            f"Sentinel TTL ({m.group(1)}) does not expire the key — "
                            "it only looks like a bound.",
                            line.strip()[:160],
                        ))
                continue

            if _CACHE_DECORATOR.search(line):
                window = _window(lines, i, 4)
                if not _MAXSIZE_KEY.search(window) and not _TTL_KEY.search(window):
                    findings.append(Finding(
                        "CR103", "medium", path, i + 1,
                        "Unbounded memoization — add maxsize= or a TTL so the "
                        "cache cannot grow without limit.",
                        line.strip()[:160],
                    ))
                continue

            m = _WILDCARD_DELETE.search(line)
            if m:
                findings.append(Finding(
                    "CR104", "medium", path, i + 1,
                    f"Wildcard key scan ('{m.group(1)}') runs KEYS across the "
                    "whole keyspace — use SCAN or a tracked index instead.",
                    line.strip()[:160],
                ))
                continue

            if _FLUSH_ALL.search(line):
                findings.append(Finding(
                    "CR105", "high", path, i + 1,
                    "Full-flush call clears every database, including keys other "
                    "services own. Delete by prefix or track keys explicitly.",
                    line.strip()[:160],
                ))

    if is_prompt:
        total = len(text)
        if total > PROMPT_CHAR_BUDGET:
            findings.append(Finding(
                "CR201", "medium", path, 1,
                f"Context file is {total:,} characters, over the "
                f"{PROMPT_CHAR_BUDGET:,} budget — split it and load sections "
                "on demand.",
                f"{total} chars",
            ))

        blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if len(b.strip()) >= BLOCK_MIN_CHARS]
        repeated = sorted({b for b, c in Counter(blocks).items() if c >= 2})
        for block in repeated:
            first = next((i + 1 for i, line in enumerate(lines)
                          if line.strip() and line.strip() in block), 1)
            findings.append(Finding(
                "CR202", "medium", path, first,
                "Identical block appears more than once — extract it to one "
                "included file instead of repeating it in the prompt.",
                block.splitlines()[0].strip()[:160],
            ))

        urls = _EXTERNAL_URL.findall(text)
        if urls:
            findings.append(Finding(
                "CR203", "low", path, 1,
                f"{len(urls)} external URL(s) inlined — move them to a "
                "reference file so the prompt carries only what it needs.",
                ", ".join(sorted(set(urls))[:3])[:160],
            ))

    return sorted(findings, key=lambda f: (f.line, f.code))


def scan_path(
    root: str | Path,
    extensions: Iterable[str] | None = None,
    skip_dirs: Iterable[str] | None = None,
) -> AuditReport:
    """Walk ``root`` and audit every matching file. Never follows symlinks."""
    exts = tuple(extensions) if extensions is not None else DEFAULT_EXTENSIONS
    skip = set(skip_dirs) if skip_dirs is not None else set(SKIP_DIRS)
    base = Path(root)
    report = AuditReport(root=str(base))

    if not base.exists():
        return report

    candidates: list[Path]
    if base.is_file():
        candidates = [base]
    else:
        candidates = []
        for p in sorted(base.rglob("*")):
            if p.is_symlink() or not p.is_file():
                continue
            if any(part in skip for part in p.relative_to(base).parts[:-1]):
                continue
            if p.suffix.lower() in exts:
                candidates.append(p)

    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        report.files_scanned += 1
        try:
            rel = str(path.relative_to(base))
        except ValueError:
            rel = str(path)
        report.findings.extend(scan_text(text, path=rel))

    report.findings.sort(key=lambda f: (f.path, f.line, f.code))
    return report
