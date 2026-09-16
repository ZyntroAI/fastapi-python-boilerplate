"""Line-ending and byte-fidelity helpers.

Everything in this module operates on **bytes**. Decoding a file to ``str`` and
re-encoding it is the single largest source of accidental whole-file rewrites:
Python text mode normalises CRLF to LF, so a two-line append lands in the diff
as every line changed. The suite therefore never decodes a file it will write
back.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Literal

EolStyle = Literal["lf", "crlf", "cr", "mixed", "none"]

TERMINATOR: dict[str, bytes] = {"lf": b"\n", "crlf": b"\r\n", "cr": b"\r"}

_TERMINATOR_NAMES: dict[bytes, str] = {v: k for k, v in TERMINATOR.items()}


def _terminator_name(terminator: bytes) -> str:
    """A symbolic name for a terminator, so serialised output is readable.

    ``repr`` would render a newline as ``'\\n'`` in JSON, which is unreadable in
    a report; ``"lf"`` is not.
    """
    return _TERMINATOR_NAMES.get(terminator, repr(terminator))


def detect_eol(data: bytes) -> EolStyle:
    """Classify the line-ending style of ``data``."""
    if not data:
        return "none"
    crlf = data.count(b"\r\n")
    cr = data.count(b"\r") - crlf
    lf = data.count(b"\n") - crlf
    present = {name for name, n in (("crlf", crlf), ("cr", cr), ("lf", lf)) if n}
    if not present:
        return "none"
    if len(present) > 1:
        return "mixed"
    return present.pop()  # type: ignore[return-value]


def dominant_terminator(data: bytes) -> bytes:
    """The terminator to use when appending to ``data``.

    A mixed-ending file resolves to its majority terminator rather than
    guessing; ``lf`` is the tie-breaker because the repo's ``.gitattributes``
    normalises to LF.
    """
    style = detect_eol(data)
    if style in TERMINATOR:
        return TERMINATOR[style]
    if style == "mixed":
        crlf = data.count(b"\r\n")
        counts = {
            "crlf": crlf,
            "cr": data.count(b"\r") - crlf,
            "lf": data.count(b"\n") - crlf,
        }
        # Ties resolve to LF: the repo's .gitattributes normalises to LF, so a
        # tie broken toward CRLF would fight the checkout.
        top = max(counts.values())
        for style_name in ("lf", "crlf", "cr"):
            if counts[style_name] == top:
                return TERMINATOR[style_name]
    return b"\n"


def ends_with_newline(data: bytes) -> bool:
    return data.endswith((b"\n", b"\r"))


@dataclass(frozen=True)
class ByteProfile:
    size: int
    eol: EolStyle
    final_newline: bool
    terminator: bytes
    sha256: str

    def as_dict(self) -> dict[str, object]:
        return {
            "size": self.size,
            "eol": self.eol,
            "final_newline": self.final_newline,
            "terminator": _terminator_name(self.terminator),
            "sha256": self.sha256,
        }


def profile(data: bytes) -> ByteProfile:
    return ByteProfile(
        size=len(data),
        eol=detect_eol(data),
        final_newline=ends_with_newline(data),
        terminator=dominant_terminator(data),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def to_bytes(text: str, terminator: bytes = b"\n", final_newline: bool = True) -> bytes:
    """Encode ``text`` using ``terminator`` as the line separator.

    Embedded newlines in ``text`` are treated as logical line breaks and
    rewritten to ``terminator``; the result is a byte string whose endings are
    uniform.
    """
    if not text:
        return b""
    body = text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    data = body.replace(b"\n", terminator)
    if final_newline and not data.endswith(terminator):
        data += terminator
    if not final_newline and data.endswith(terminator):
        data = data[: -len(terminator)]
    return data


def normalize_terminators(data: bytes, terminator: bytes) -> bytes:
    """Rewrite every line ending to ``terminator`` without altering content."""
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n").replace(b"\n", terminator)


def matches_final_newline(data: bytes, want: bool) -> bool:
    return ends_with_newline(data) is want
