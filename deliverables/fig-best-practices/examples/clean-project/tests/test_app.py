"""Clean example tests."""

from __future__ import annotations


def test_card_props_shape() -> None:
    props = {"title": "Hello", "body": "World"}
    assert set(props) == {"title", "body"}


def test_tokens_reference_only_vars() -> None:
    tokens = ["var(--color-brand-primary)", "var(--space-4)"]
    assert all(t.startswith("var(--") for t in tokens)
