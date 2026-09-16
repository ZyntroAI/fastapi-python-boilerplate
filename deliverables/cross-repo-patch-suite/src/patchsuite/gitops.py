"""Git operation wrappers that surface the failure modes rather than hiding them.

``git am`` and ``git apply`` fail on whitespace- and EOL-grounds far more often
than on real content conflict, and the reported reason ("patch does not apply")
is the same in every case. These wrappers pre-diagnose the cause so the fix is
obvious, and they never leave the work tree in a half-applied state.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from . import eol


@dataclass
class CommandResult:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def as_dict(self) -> dict[str, object]:
        return {
            "args": self.args,
            "returncode": self.returncode,
            "stdout": self.stdout.strip(),
            "stderr": self.stderr.strip(),
            "ok": self.ok,
        }


def _run(args: list[str], cwd: str | Path | None = None) -> CommandResult:
    if shutil.which(args[0]) is None:
        return CommandResult(args, 127, "", f"{args[0]} not found on PATH")
    proc = subprocess.run(
        args, cwd=str(cwd) if cwd else None, capture_output=True, text=True, check=False
    )
    return CommandResult(args, proc.returncode, proc.stdout, proc.stderr)


def git_available() -> bool:
    return shutil.which("git") is not None


def is_work_tree(path: str | Path) -> bool:
    return _run(["git", "rev-parse", "--is-inside-work-tree"], cwd=path).stdout.strip() == "true"


@dataclass
class PatchDiagnosis:
    applies: bool
    code: int
    reason: str
    likely_cause: str
    suggested_fix: str

    def as_dict(self) -> dict[str, object]:
        return {
            "applies": self.applies,
            "code": self.code,
            "reason": self.reason,
            "likely_cause": self.likely_cause,
            "suggested_fix": self.suggested_fix,
        }


_CAUSE_TABLE: list[tuple[tuple[str, ...], str, str]] = [
    (
        ("whitespace", "trailing whitespace", "space before tab"),
        "Whitespace drift while the repo enforces whitespace rules at apply time.",
        "Re-check out the target and re-apply with `git apply --whitespace=nowarn`, "
        "or fix the payload's trailing whitespace at the source.",
    ),
    (
        ("no such file", "does not exist in index"),
        "The patch targets a path that is not present on this branch.",
        "Confirm the base branch — a patch written against a feature branch will "
        "not apply to main if the file only exists on the branch.",
    ),
    (
        ("already exists",),
        "The patch creates a file that is already there.",
        "Decide explicitly: restore/overwrite, or keep the existing file and place "
        "the new work beside it rather than on top of it.",
    ),
    (
        ("does not match index", "index mismatch", "recorded in its index", "hand edit your patch"),
        "The blob hashes in the patch header no longer match the working tree.",
        "Drop the index line with `git am --3way` after a fetch, or regenerate the "
        "patch from the current base so the hashes are real.",
    ),
    (
        ("corrupt patch", "malformed", "unexpected line"),
        "The patch file itself is malformed — usually CRLF line endings or a "
        "missing trailing newline in the source file at patch time.",
        "Normalise the patch to LF and re-apply; if the source file is CRLF and "
        "unterminated, use the byte-append path instead of `git am`.",
    ),
]


def diagnose_patch_failure(stderr: str, code: int) -> PatchDiagnosis:
    low = stderr.lower()
    for keys, cause, fix in _CAUSE_TABLE:
        if any(k in low for k in keys):
            return PatchDiagnosis(False, code, stderr.strip(), cause, fix)
    return PatchDiagnosis(
        False,
        code,
        stderr.strip(),
        "Unclassified — the reported reason does not match a known EOL, whitespace, "
        "index, or path failure.",
        "Inspect the patch header and the target file's current bytes directly; the "
        "three-way attempt (`git apply --3way`) usually names the true cause.",
    )


def check_patch(patch: Path, target: str | Path) -> PatchDiagnosis:
    """`git apply --check` with a diagnosis attached."""
    result = _run(["git", "apply", "--check", str(patch)], cwd=target)
    if result.ok:
        return PatchDiagnosis(True, 0, "", "Patch applies cleanly.", "No action needed.")
    return diagnose_patch_failure(result.stderr or result.stdout, result.returncode)


def apply_patch(patch: Path, target: str | Path, three_way: bool = False) -> CommandResult:
    args = ["git", "apply"]
    if three_way:
        args.append("--3way")
    args.append(str(patch))
    return _run(args, cwd=target)


def apply_mailbox(patch: Path, target: str | Path) -> CommandResult:
    """`git am` in a scratch-safe order: `--abort` first so a prior failure cannot
    wedge the next one."""
    _run(["git", "am", "--abort"], cwd=target)
    return _run(["git", "am", "--3way", str(patch)], cwd=target)


@dataclass
class EolRisk:
    path: str
    eol: str
    final_newline: bool
    at_risk: bool
    reason: str

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "eol": self.eol,
            "final_newline": self.final_newline,
            "at_risk": self.at_risk,
            "reason": self.reason,
        }


def audit_eol_risk(root: str | Path, patterns: tuple[str, ...] = ("*.yml", "*.yaml")) -> list[EolRisk]:
    """Flag files whose EOL state will break ``git am``.

    The dangerous combination is CRLF **and** no trailing newline: the patch
    reports "does not apply" while ``git apply --check`` passes, which sends
    debugging in the wrong direction.
    """
    base = Path(root)
    risks: list[EolRisk] = []
    for pattern in patterns:
        for path in sorted(base.rglob(pattern)):
            if ".git" in path.parts:
                continue
            raw = path.read_bytes()
            style = eol.detect_eol(raw)
            final = eol.ends_with_newline(raw)
            at_risk = style in ("crlf", "mixed") and not final
            if at_risk:
                reason = (
                    f"{style.upper()} line endings with no trailing newline — "
                    "`git am` will report 'patch does not apply' even when "
                    "`git apply --check` passes."
                )
            elif style in ("crlf", "mixed"):
                reason = f"{style.upper()} line endings — patches must be generated with EOL fidelity."
            else:
                reason = "LF, trailing newline present — safe."
            risks.append(EolRisk(str(path.relative_to(base)), style, final, at_risk, reason))
    return risks


def current_branch(target: str | Path) -> str:
    return _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=target).stdout.strip()


def head_sha(target: str | Path, short: bool = True) -> str:
    args = ["git", "rev-parse", "--short", "HEAD"] if short else ["git", "rev-parse", "HEAD"]
    return _run(args, cwd=target).stdout.strip()


@dataclass
class DirtyState:
    dirty: bool
    entries: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {"dirty": self.dirty, "entries": self.entries}


def working_tree_state(target: str | Path) -> DirtyState:
    result = _run(["git", "status", "--porcelain"], cwd=target)
    entries = [ln for ln in result.stdout.splitlines() if ln.strip()]
    return DirtyState(dirty=bool(entries), entries=entries)
