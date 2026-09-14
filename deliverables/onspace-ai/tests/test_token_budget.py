"""Tests: token budget"""
from app.context_compiler import compile_context
from app.token_budget import TokenBudget, MODEL_LIMITS


def test_model_limits_default():
    assert MODEL_LIMITS["default"] == 128000
    assert TokenBudget("gpt-4o").max == 128000
    assert TokenBudget("claude-3-opus").max == 200000


def test_check_within_budget():
    b = TokenBudget("gpt-4o")
    assert b.check(1000) is True


def test_check_over_budget():
    b = TokenBudget("gpt-4o")
    assert b.check(200000) is False


def test_truncate_drops_old_messages():
    b = TokenBudget("mini")  # 32k limit
    # เนื้อหายาวมาก + แต่ละข้อความต่างกัน (กัน dedup ยุบรวม)
    msgs = [
        {"role": "user", "content": "a" * 100000},
        {"role": "user", "content": "b" * 100000},
        {"role": "user", "content": "c" * 100000},
    ]
    ctx = compile_context("sys", msgs, max_tokens=1000000)
    assert ctx["estimated_tokens"] > b.max  # เกิน
    out = b.truncate(ctx)
    assert out["estimated_tokens"] <= b.max


def test_reject_reason_message():
    b = TokenBudget("mini")
    assert "exceeds" in b.reject_reason(50000)
