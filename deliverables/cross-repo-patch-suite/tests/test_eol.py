"""Line-ending detection and conversion."""

from __future__ import annotations

from patchsuite import eol


def test_detect_eol_lf():
    assert eol.detect_eol(b"a\nb\n") == "lf"


def test_detect_eol_crlf():
    assert eol.detect_eol(b"a\r\nb\r\n") == "crlf"


def test_detect_eol_cr():
    assert eol.detect_eol(b"a\rb\r") == "cr"


def test_detect_eol_mixed():
    assert eol.detect_eol(b"a\r\nb\nc\r\n") == "mixed"


def test_detect_eol_empty():
    assert eol.detect_eol(b"") == "none"


def test_detect_eol_single_line_no_terminator():
    assert eol.detect_eol(b"name: Sync") == "none"


def test_dominant_terminator_matches_style():
    assert eol.dominant_terminator(b"a\r\nb\r\n") == b"\r\n"
    assert eol.dominant_terminator(b"a\nb\n") == b"\n"


def test_dominant_terminator_mixed_resolves_to_majority():
    # three CRLF, one LF -> CRLF wins
    data = b"a\r\nb\r\nc\r\nD\n"
    assert eol.dominant_terminator(data) == b"\r\n"


def test_dominant_terminator_breaks_ties_toward_lf():
    # one of each -> LF, because .gitattributes normalises to LF
    assert eol.dominant_terminator(b"a\r\nb\n") == b"\n"


def test_dominant_terminator_empty_defaults_lf():
    assert eol.dominant_terminator(b"") == b"\n"


def test_ends_with_newline():
    assert eol.ends_with_newline(b"a\n")
    assert eol.ends_with_newline(b"a\r\n")
    assert not eol.ends_with_newline(b"a")


def test_to_bytes_lf():
    assert eol.to_bytes("a\nb") == b"a\nb\n"


def test_to_bytes_crlf():
    assert eol.to_bytes("a\nb", terminator=b"\r\n") == b"a\r\nb\r\n"


def test_to_bytes_normalises_input_endings():
    # CRLF in the source string must not survive as a double terminator
    assert eol.to_bytes("a\r\nb", terminator=b"\r\n") == b"a\r\nb\r\n"


def test_to_bytes_no_final_newline():
    assert eol.to_bytes("a\nb", final_newline=False) == b"a\nb"


def test_to_bytes_strips_final_newline_when_disabled():
    assert eol.to_bytes("a\nb\n", final_newline=False) == b"a\nb"


def test_to_bytes_empty():
    assert eol.to_bytes("") == b""


def test_to_bytes_unicode():
    assert eol.to_bytes("ชื่อ\nไฟล์") == "ชื่อ\nไฟล์\n".encode()


def test_normalize_terminators_crlf_to_lf():
    assert eol.normalize_terminators(b"a\r\nb\r\n", b"\n") == b"a\nb\n"


def test_normalize_terminators_lf_to_crlf():
    assert eol.normalize_terminators(b"a\nb\n", b"\r\n") == b"a\r\nb\r\n"


def test_normalize_preserves_content():
    data = "hello: world\nlist:\n  - a\n".encode()
    assert eol.normalize_terminators(data, b"\r\n").replace(b"\r\n", b"\n") == data


def test_profile_records_bytes_and_hash():
    p = eol.profile(b"a\r\nb")
    assert p.size == 4
    assert p.eol == "crlf"
    assert p.final_newline is False
    assert len(p.sha256) == 64


def test_profile_as_dict_roundtrip():
    p = eol.profile(b"a\n")
    d = p.as_dict()
    assert d["eol"] == "lf"
    assert d["terminator"] == "lf", "terminators serialise symbolically, not as escape text"
    assert d["final_newline"] is True


def test_profile_as_dict_signals_crlf_by_name():
    assert eol.profile(b"a\r\n").as_dict()["terminator"] == "crlf"


def test_matches_final_newline():
    assert eol.matches_final_newline(b"a\n", True)
    assert eol.matches_final_newline(b"a", False)
