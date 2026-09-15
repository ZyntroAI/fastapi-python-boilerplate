"""Broken example tests — TESTING passes here on purpose.

The standard requires tests to exist; the other criteria are where this
project fails.
"""

from __future__ import annotations


def test_card_renders_a_title() -> None:
    assert "title" in {"title": "x"}


def test_settings_exposes_a_token() -> None:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    import settings

    assert isinstance(settings.get_token(), str)
