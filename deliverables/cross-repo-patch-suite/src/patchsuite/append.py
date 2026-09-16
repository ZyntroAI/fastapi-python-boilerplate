"""Byte-exact appends.

The contract: an append may add bytes and may insert **at most one** terminator
to close an unterminated final line. Every other pre-existing byte must survive
identical. ``verify_append`` is what proves it, and it is the check to run
before committing any append to a file you do not own.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path

from . import eol


@dataclass
class AppendResult:
    path: str
    bytes_before: int
    bytes_after: int
    existing_eol: str
    payload_eol: str
    aligned: bool
    terminator_added: bool
    dry_run: bool

    @property
    def grew_by(self) -> int:
        return self.bytes_after - self.bytes_before

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "bytes_before": self.bytes_before,
            "bytes_after": self.bytes_after,
            "grew_by": self.grew_by,
            "existing_eol": self.existing_eol,
            "payload_eol": self.payload_eol,
            "aligned": self.aligned,
            "terminator_added": self.terminator_added,
            "dry_run": self.dry_run,
        }


def plan_append(existing: bytes, payload_text: str, align: bool = True) -> tuple[bytes, bool]:
    """Return ``(new_content, terminator_added)``. Pure — performs no I/O.

    When ``align`` is set the payload is rewritten to the existing file's
    dominant terminator, so a CRLF file stays CRLF and the diff shows only the
    appended lines.
    """
    existing_terminator = eol.dominant_terminator(existing)
    payload = eol.to_bytes(payload_text, terminator=b"\n", final_newline=True)
    if align and existing_terminator != b"\n":
        payload = payload.replace(b"\n", existing_terminator)

    terminator_added = bool(existing) and not eol.ends_with_newline(existing)
    out = existing + existing_terminator if terminator_added else existing
    return out + payload, terminator_added


def append_text(
    path: str | Path,
    payload_text: str,
    *,
    align: bool = True,
    dry_run: bool = False,
) -> AppendResult:
    """Append ``payload_text`` to ``path`` without disturbing existing bytes."""
    p = Path(path)
    existing = p.read_bytes() if p.exists() else b""
    new_content, terminator_added = plan_append(existing, payload_text, align=align)
    if not dry_run:
        p.write_bytes(new_content)
    return AppendResult(
        path=str(p),
        bytes_before=len(existing),
        bytes_after=len(new_content),
        existing_eol=eol.detect_eol(existing),
        payload_eol=eol.detect_eol(new_content[len(existing) :]),
        aligned=align,
        terminator_added=terminator_added,
        dry_run=dry_run,
    )


@dataclass(frozen=True)
class AppendVerification:
    ok: bool
    prefix_identical: bool
    terminator_added: bool
    appended_lines: int
    changed_line_numbers: list[int]

    def as_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "prefix_identical": self.prefix_identical,
            "terminator_added": self.terminator_added,
            "appended_lines": self.appended_lines,
            "changed_line_numbers": self.changed_line_numbers,
        }


def verify_append(before: bytes, after: bytes) -> AppendVerification:
    """Prove that ``after`` is ``before`` plus appended content and nothing else.

    Fails when the pre-existing region was rewritten — the exact failure the
    text-mode round-trip produces.
    """
    if after == before:
        return AppendVerification(True, True, False, 0, [])

    # A terminator is *inserted* when the file did not end with one: `before` is
    # still an exact prefix, and the very next byte in `after` is that terminator.
    prefix_identical = after.startswith(before)
    terminator_added = False
    if prefix_identical:
        rest = after[len(before) :]
        if rest[:1] in (b"\n", b"\r"):
            terminator_added = True
    elif len(after) > len(before):
        for term in (b"\r\n", b"\n", b"\r"):
            if after.startswith(before + term):
                prefix_identical = True
                terminator_added = True
                break

    before_lines = before.decode("utf-8", "replace").splitlines()
    after_lines = after.decode("utf-8", "replace").splitlines()
    changed: list[int] = []
    for i, (a, b) in enumerate(zip(before_lines, after_lines)):
        if a != b:
            changed.append(i + 1)

    appended_lines = max(0, len(after_lines) - len(before_lines) - len(changed))
    ok = prefix_identical and not changed
    return AppendVerification(ok, prefix_identical, terminator_added, appended_lines, changed)


def diff_stat(before: bytes, after: bytes, name: str = "file") -> dict[str, int]:
    """How many lines the diff touches — the number that exposes a whole-file rewrite."""
    a = before.decode("utf-8", "replace").splitlines(keepends=True)
    b = after.decode("utf-8", "replace").splitlines(keepends=True)
    added = removed = 0
    for line in difflib.unified_diff(a, b, n=0):
        if line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    return {"added": added, "removed": removed, "total_touched": added + removed}


def safe_read(path: str | Path) -> bytes:
    """Read a file as bytes, returning ``b''`` when it does not exist."""
    p = Path(path)
    return p.read_bytes() if p.exists() else b""
