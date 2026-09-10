"""Runtime tool switcher.

Lets a caller switch which "tool" the backend presents as active (pm_csv,
billing, settings) at runtime — useful for a UI tool switcher or for routing
an integration to a different feature area without redeploying. The chosen
tool is persisted so a restart keeps the selection.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from .config import get_settings

_STATE_FILE = Path(
    os.getenv("TOOL_STATE_FILE", str(Path(__file__).resolve().parent.parent / "tool_state.json"))
)

KNOWN_TOOLS = ("pm_csv", "billing", "settings")


def _load_state() -> str:
    try:
        with open(_STATE_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return str(data.get("active_tool", "")).lower()
    except (OSError, ValueError, TypeError):
        return ""


def _save_state(tool: str) -> None:
    _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_STATE_FILE, "w", encoding="utf-8") as fh:
        json.dump({"active_tool": tool}, fh, indent=2)


def current_tool() -> str:
    """Return the active tool, preferring persisted state over env default."""
    persisted = _load_state()
    if persisted in KNOWN_TOOLS:
        return persisted
    default = get_settings().active_tool.lower()
    return default if default in KNOWN_TOOLS else KNOWN_TOOLS[0]


def list_tools() -> list[str]:
    return list(KNOWN_TOOLS)


def set_tool(tool: str) -> str:
    """Switch the active tool. Raises ValueError for unknown tools."""
    tool = tool.strip().lower()
    if tool not in KNOWN_TOOLS:
        raise ValueError(
            f"Unknown tool {tool!r}; expected one of {KNOWN_TOOLS}"
        )
    _save_state(tool)
    return tool
