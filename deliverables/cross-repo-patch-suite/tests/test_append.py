"""Byte-exact append behaviour — the heart of the suite."""

from __future__ import annotations

import hashlib

from patchsuite import append_text, diff_stat, plan_append, safe_read, verify_append


def test_append_to_lf_file_adds_only_the_payload():
    before = b"line one\nline two\n"
    after, terminator_added = plan_append(before, "line three")
    assert after == b"line one\nline two\nline three\n"
    assert terminator_added is False
    assert verify_append(before, after).ok


def test_append_preserves_crlf_endings():
    before = b"name: Sync\r\n\r\non:\r\n  push:\r\n"
    after, _ = plan_append(before, "jobs:\n  sync:")
    assert after.startswith(before)
    assert b"\r\n" in after[len(before) :]
    assert b"\n" not in after.replace(b"\r\n", b"")  # no bare LF introduced
    assert verify_append(before, after).ok


def test_append_closes_an_unterminated_final_line():
    before = b"name: Sync\non: push"  # no trailing newline
    after, terminator_added = plan_append(before, "jobs: {}")
    assert terminator_added is True
    assert after == b"name: Sync\non: push\njobs: {}\n"
    assert verify_append(before, after).ok


def test_append_closes_unterminated_crlf_final_line():
    before = b"name: Sync\r\non: push"
    after, terminator_added = plan_append(before, "jobs: {}")
    assert terminator_added is True
    assert after == b"name: Sync\r\non: push\r\njobs: {}\r\n"
    assert verify_append(before, after).ok


def test_append_to_empty_file():
    after, terminator_added = plan_append(b"", "first line")
    assert after == b"first line\n"
    assert terminator_added is False


def test_append_does_not_duplicate_a_final_newline():
    before = b"a\n"
    after, _ = plan_append(before, "b")
    assert after == b"a\nb\n"
    assert after.count(b"a\n") == 1


def test_append_no_align_keeps_payload_lf_in_crlf_file():
    before = b"a\r\nb\r\n"
    after, _ = plan_append(before, "c", align=False)
    assert after == b"a\r\nb\r\nc\n"


def test_append_unicode_payload():
    before = b"# Notes\n"
    after, _ = plan_append(before, "ชื่อ: ทดสอบ")
    assert after == "# Notes\nชื่อ: ทดสอบ\n".encode()


def test_verify_detects_a_rewritten_prefix():
    before = b"a\nb\n"
    after = b"a\nB\nc\n"  # 'b' was changed, not merely appended to
    result = verify_append(before, after)
    assert result.ok is False
    assert result.prefix_identical is False
    assert result.changed_line_numbers == [2]


def test_verify_detects_eol_normalisation_of_existing_lines():
    """The exact failure a text-mode round-trip produces."""
    before = b"a\r\nb\r\n"
    after = b"a\nb\nc\n"  # existing CRLF silently became LF
    result = verify_append(before, after)
    assert result.ok is False
    assert result.prefix_identical is False


def test_verify_accepts_an_identical_file():
    result = verify_append(b"a\n", b"a\n")
    assert result.ok is True
    assert result.appended_lines == 0


def test_verify_counts_appended_lines():
    before = b"a\n"
    after = b"a\nb\nc\n"
    result = verify_append(before, after)
    assert result.ok is True
    assert result.appended_lines == 2


def test_verify_recognises_terminator_insertion_as_safe():
    before = b"a"
    after = b"a\nb\n"
    result = verify_append(before, after)
    assert result.ok is True
    assert result.terminator_added is True


def test_diff_stat_shows_a_two_line_append_as_two_lines():
    before = b"a\nb\n"
    after = before + b"c\nd\n"
    stat = diff_stat(before, after)
    assert stat["added"] == 2
    assert stat["removed"] == 0


def test_diff_stat_exposes_a_whole_file_rewrite():
    """An EOL-normalising round-trip touches every line — this catches it."""
    before = b"a\r\nb\r\nc\r\n"
    after = b"a\nb\nc\nd\n"
    stat = diff_stat(before, after)
    assert stat["removed"] == 3, "every existing line should register as changed"
    assert stat["added"] == 4


def test_append_text_writes_bytes_and_reports_growth(tmp_path):
    target = tmp_path / "f.txt"
    target.write_bytes(b"one\r\n")
    result = append_text(target, "two")
    assert target.read_bytes() == b"one\r\ntwo\r\n"
    assert result.grew_by == len(b"two\r\n")
    assert result.existing_eol == "crlf"
    assert result.dry_run is False


def test_append_text_dry_run_does_not_write(tmp_path):
    target = tmp_path / "f.txt"
    target.write_bytes(b"one\n")
    result = append_text(target, "two", dry_run=True)
    assert target.read_bytes() == b"one\n"
    assert result.dry_run is True
    assert result.bytes_after > result.bytes_before


def test_append_text_creates_a_missing_file(tmp_path):
    target = tmp_path / "new.txt"
    append_text(target, "hello")
    assert target.read_bytes() == b"hello\n"


def test_two_appends_stay_byte_faithful(tmp_path):
    target = tmp_path / "f.txt"
    target.write_bytes(b"a\r\n")
    append_text(target, "b")
    append_text(target, "c")
    assert target.read_bytes() == b"a\r\nb\r\nc\r\n"


def test_append_result_as_dict_is_json_safe(tmp_path):
    import json

    target = tmp_path / "f.txt"
    target.write_bytes(b"a\n")
    result = append_text(target, "b", dry_run=True)
    assert json.loads(json.dumps(result.as_dict()))["grew_by"] == 2


def test_safe_read_missing_file_is_empty():
    assert safe_read("/nonexistent/path/xyz") == b""


def test_appending_a_large_payload_preserves_prefix(tmp_path):
    target = tmp_path / "f.txt"
    original = ("line %d\n" % i for i in range(500))
    target.write_text("".join(original), encoding="utf-8", newline="")
    before = target.read_bytes()
    append_text(target, "\n".join(f"new {i}" for i in range(200)))
    after = target.read_bytes()
    assert after.startswith(before)
    assert verify_append(before, after).ok


def test_append_preserves_sha_of_the_original_prefix(tmp_path):
    target = tmp_path / "f.txt"
    target.write_bytes(b"keep\r\nme\r\n")
    before = target.read_bytes()
    append_text(target, "added")
    after = target.read_bytes()
    assert hashlib.sha256(after[: len(before)]).hexdigest() == hashlib.sha256(before).hexdigest()
