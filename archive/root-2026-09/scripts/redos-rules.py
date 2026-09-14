"""
ReDoS Detection Rules — Python Edition
CWE-1333: Inefficient Regular Expression Complexity
Version: 1.0 | 2026-09-09
"""
import re
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ReDoSRule:
    id: str
    severity: str
    name: str
    pattern: re.Pattern
    message: str
    fix_example: str

REDOS_RULES: List[ReDoSRule] = [
    ReDoSRule(
        id="RD-001",
        severity="CRITICAL",
        name="Nested Quantifiers",
        pattern=re.compile(r"\([^()]*[+*][^()]*\)\s*[+*]\??"),
        message="Quantifier ซ้อนกัน เช่น (A+)* ทำให้เกิด Backtracking แบบเลขชี้กำลัง",
        fix_example="เปลี่ยน r'^(\\w+\\s?)*$' เป็น r'^((?=(\\w+))\\2\\s?)*$'"
    ),
    ReDoSRule(
        id="RD-002",
        severity="HIGH",
        name="Overlapping Alternation",
        pattern=re.compile(r"\([^)|]+\|[^)|]+\|[^)|]+\)\s*[+*]"),
        message="ทางเลือกที่ซ้อนทับกัน เพิ่มเวลาประมวลผลแบบเลขชี้กำลัง",
        fix_example="ลดทางเลือกให้ไม่ซ้อนทับกัน หรือเรียงจากยาวไปสั้น"
    ),
    ReDoSRule(
        id="RD-003",
        severity="HIGH",
        name="Unbounded Quantifier + User Input",
        pattern=re.compile(r"(re\.|regex|search|match|fullmatch).*(request|input|form|query)"),
        message="RegEx กับข้อมูลผู้ใช้โดยไม่จำกัดความยาว — เสี่ยง ReDoS",
        fix_example="ตรวจความยาวก่อน: if len(s) > 1000: raise ValueError"
    ),
    ReDoSRule(
        id="RD-004",
        severity="MEDIUM",
        name="Large Minimum Quantifier",
        pattern=re.compile(r"[+*]\{(\d{2,}),\}"),
        message="Quantifier ขั้นต่ำมากโดยไม่มีขอบบน — อาจช้ามาก",
        fix_example="กำหนดขอบเขตบนเสมอ: {min,max}"
    )
]

def detect_redos(pattern: str) -> List[Dict]:
    """ตรวจจับรูปแบบ ReDoS จากสตริง RegEx"""
    findings = []
    for rule in REDOS_RULES:
        if rule.pattern.search(pattern):
            findings.append({
                "id": rule.id,
                "severity": rule.severity,
                "name": rule.name,
                "message": rule.message,
                "fix_example": rule.fix_example
            })
    return findings`