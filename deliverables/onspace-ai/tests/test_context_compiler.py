"""Tests: context compiler"""
from app.context_compiler import (
    clean_text,
    compile_context,
    deduplicate_messages,
    estimate_tokens,
    trim_history,
)


def test_clean_text_collapses_whitespace():
    assert clean_text("  a\n\n\n  b  ") == "a\nb"


def test_estimate_tokens():
    assert estimate_tokens("") == 0
    assert estimate_tokens("hello world") > 0


def test_deduplicate_consecutive_only():
    msgs = [
        {"role": "user", "content": "a"},
        {"role": "user", "content": "a"},  # ซ้ำติดกัน → ตัด
        {"role": "assistant", "content": "b"},
        {"role": "user", "content": "a"},  # ไม่ติดกัน → เก็บ
    ]
    out = deduplicate_messages(msgs)
    assert len(out) == 3


def test_trim_history_keeps_last_n():
    msgs = [{"role": "user", "content": f"m{i}"} for i in range(10)]
    out = trim_history(msgs, max_turns=3)
    assert len(out) == 3
    assert out[-1]["content"] == "m9"


def test_compile_context_counts_tokens():
    ctx = compile_context("sys", [{"role": "user", "content": "hello"}], max_tokens=100)
    assert ctx["estimated_tokens"] > 0
    assert ctx["over_budget"] is False
    assert ctx["system"] == "sys"


def test_compile_context_over_budget_flag():
    big = "x" * 5000
    ctx = compile_context(big, [{"role": "user", "content": "y" * 5000}], max_tokens=10)
    assert ctx["over_budget"] is True
