"""Context Compiler — clean/dedup/trim context before it reaches a provider."""
from __future__ import annotations

import re
from typing import Dict, List

# Token estimate: ~3.5 chars/token. Deliberately rough — this is a guardrail,
# not a billing figure.
CHARS_PER_TOKEN = 3.5


def clean_text(text: str) -> str:
    """Collapse runs of spaces and drop blank lines."""
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    return "\n".join(ln for ln in lines if ln)


def deduplicate_messages(messages: List[Dict]) -> List[Dict]:
    """Drop consecutive duplicate messages (keeps the first of each run)."""
    if not messages:
        return []
    out = [messages[0]]
    for m in messages[1:]:
        if (m.get("role"), m.get("content")) != (out[-1].get("role"), out[-1].get("content")):
            out.append(m)
    return out


def estimate_tokens(text: str) -> int:
    """Estimate tokens from UTF-8 byte length — fast and language-neutral."""
    if not text:
        return 0
    return int(len(text.encode("utf-8")) / CHARS_PER_TOKEN) + 1


def trim_history(messages: List[Dict], max_turns: int) -> List[Dict]:
    """Keep only the last N turns (plus any system messages)."""
    if max_turns <= 0 or len(messages) <= max_turns:
        return messages
    sys_msgs = [m for m in messages if m.get("role") == "system"]
    rest = [m for m in messages if m.get("role") != "system"]
    return sys_msgs + rest[-max_turns:]


def compile_context(
    system: str, messages: List[Dict], max_tokens: int, max_turns: int = 20
) -> Dict:
    """Combine system + messages → clean/dedup/trim with an estimated token count."""
    sys_clean = clean_text(system)
    msgs = [
        {"role": m.get("role", "user"), "content": clean_text(m.get("content", ""))}
        for m in messages
    ]
    msgs = deduplicate_messages(msgs)
    msgs = trim_history(msgs, max_turns)

    total = estimate_tokens(sys_clean) + sum(estimate_tokens(m["content"]) for m in msgs)
    return {
        "system": sys_clean,
        "messages": msgs,
        "estimated_tokens": total,
        "over_budget": total > max_tokens,
    }
