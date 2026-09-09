"""Context Compiler — trim/dedup/compress context ก่อนส่ง provider"""
from __future__ import annotations

import re
from typing import Dict, List

# ประมาณ tokens: ~4 ตัวอักษร/โทเคน (ภาษาไทย/ผสมระวัง แต่ใช้เป็น estimate พอ)
CHARS_PER_TOKEN = 3.5


def clean_text(text: str) -> str:
    """Trim whitespace + ลบบรรทัดว่างซ้ำซ้อน"""
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    # ตัดบรรทัดว่างออกทั้งหมด (ยุบ \n ซ้ำเป็นบรรทัดเดียว)
    return "\n".join(ln for ln in lines if ln)


def deduplicate_messages(messages: List[Dict]) -> List[Dict]:
    """ลบข้อความซ้ำติดกัน (เก็บเฉพาะ instance แรกของ sequence)"""
    if not messages:
        return []
    out = [messages[0]]
    for m in messages[1:]:
        if (m.get("role"), m.get("content")) != (out[-1].get("role"), out[-1].get("content")):
            out.append(m)
    return out


def estimate_tokens(text: str) -> int:
    """ประมาณ token จากจำนวน byte (UTF-8) — ใช้เป็น estimate เร็ว"""
    if not text:
        return 0
    return int(len(text.encode("utf-8")) / CHARS_PER_TOKEN) + 1


def trim_history(messages: List[Dict], max_turns: int) -> List[Dict]:
    """เก็บเฉพาะ last N turns (ตัดหัวทิ้งก่อน)"""
    if max_turns <= 0 or len(messages) <= max_turns:
        return messages
    # เก็บ system (ถ้ามี role system แรก) + last N turns
    sys_msgs = [m for m in messages if m.get("role") == "system"]
    rest = [m for m in messages if m.get("role") != "system"]
    return sys_msgs + rest[-max_turns:]


def compile_context(system: str, messages: List[Dict], max_tokens: int, max_turns: int = 20) -> Dict:
    """รวม system + messages → clean/dedup/trim พร้อมนับ estimated_tokens"""
    sys_clean = clean_text(system)
    msgs = [{"role": m.get("role", "user"), "content": clean_text(m.get("content", ""))} for m in messages]
    msgs = deduplicate_messages(msgs)
    msgs = trim_history(msgs, max_turns)

    total = estimate_tokens(sys_clean) + sum(estimate_tokens(m["content"]) for m in msgs)
    return {
        "system": sys_clean,
        "messages": msgs,
        "estimated_tokens": total,
        "over_budget": total > max_tokens,
    }
