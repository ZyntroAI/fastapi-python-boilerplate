#!/usr/bin/env python3
"""
แยกส่วนข้อมูลจากภาพ: Zyntro AI — Self-Verifying DevOps & Clean Package Architecture
สร้างเอกสาร/โครงสร้างจากภาพอัตโนมัติ
ใช้: python scripts/architecture-extract.py image.png > docs/architecture-summary.md
"""
import sys
import re
from pathlib import Path

# โครงสร้างที่สกัดจากภาพ
ARCHITECTURE = {
    "title": "Zyntro AI — Self-Verifying DevOps & Clean Package Architecture",
    "version": "1.0",
    "sections": {
        "core_pillars": [
            "Self-Verifying DevOps",
            "Clean Package Architecture",
            "Secure & Observable End-to-End"
        ],
        "left_column_repo_structure": {
            "layer": "Clean Package & Structure",
            "components": [
                "zyntro-core",
                "zyntro-sdk",
                "zyntro-deploy",
                "zyntro-ai",
                "zyntro-monitor",
                "zyntro-gate",
                "zyntro-log",
                "zyntro-verify"  # ✅ จุดสำคัญ — ตรวจสอบเอง
            ],
            "highlight": "zyntro-verify → ยืนยันความถูกต้องอัตโนมัติ"
        },
        "center_devops_pipeline": {
            "phase": "CI/CD & Security Pipeline",
            "stages": [
                "Code → Lint/Format",
                "Unit Test → Coverage",
                "Build → SBOM/Provenance",
                "Scan → Secret/SAST/License",
                "Sign → Attestation/Signature",
                "Deploy → Verified Gate",
                "Monitor → Telemetry/Alert"
            ],
            "enforcement": "Policy-as-Code / Branch Protection / Signed Commits"
        },
        "right_tools_security": {
            "category": "DevOps & Security Toolchain",
            "components": {
                "scanning": ["CodeQL", "Trivy", "Dependabot", "Semgrep"],
                "signing": ["Sigstore/Cosign", "Gitsign"],
                "supply_chain": ["SLSA Framework", "SBOM", "Provenance"],
                "monitoring": ["Prometheus", "Grafana", "OpenTelemetry"],
                "identity": ["OIDC", "Short-Lived Tokens", "MFA"]
            }
        },
        "bottom_foundations": [
            "Zero Trust",
            "Least Privilege",
            "Immutable Infrastructure",
            "Audit-Ready",
            "Reproducible Builds"
        ]
    },
    "key_principles": [
        "ทุกชิ้นส่วนตรวจสอบได้ — ไม่เชื่อใจโดยพลการ",
        "ลายเซ็นทุกการเปลี่ยนแปลง — ตรวจสอบย้อนกลับได้",
        "แยกส่วนชัดเจน — แก้ไข/ทดสอบทีละส่วน",
        "ปลอดภัยฝังในตัว — ไม่ใช่เพิ่มทีหลัง",
        "ตรวจสอบเองได้ — ไม่ต้องรอคนอนุมัติทุกครั้ง"
    ]
}

def generate_markdown():
    """ส่งออกเป็นเอกสาร Markdown ที่อ่านง่าย"""
    md = [
        "# 🏗️ Zyntro AI — สถาปัตยกรรมระบบ",
        "",
        f"> {ARCHITECTURE['title']}",
        f"> เวอร์ชัน: {ARCHITECTURE['version']}",
        "",
        "---",
        "",
        "## 🎯 หลักการหลัก",
    ]
    
    for p in ARCHITECTURE["core_pillars"]:
        md.append(f"- ✅ {p}")
    
    md.extend([
        "",
        "---",
        "",
        "## 📦 โครงสร้างแพ็กเกจหลัก",
        "| ชื่อ | หน้าที่ |",
        "|---|---|",
    ])
    
    for comp in ARCHITECTURE["sections"]["left_column_repo_structure"]["components"]:
        note = "🔍 ตรวจสอบความถูกต้อง" if comp == "zyntro-verify" else "โมดูลหลัก"
        md.append(f"| `{comp}` | {note} |")
    
    md.extend([
        "",
        "## 🔄 ขั้นตอน DevOps & CI/CD",
    ])
    
    for i, stage in enumerate(ARCHITECTURE["sections"]["center_devops_pipeline"]["stages"], 1):
        md.append(f"{i}. {stage}")
    
    md.extend([
        "",
        "## 🛡️ ชุดเครื่องมือความปลอดภัย",
    ])
    
    for cat, tools in ARCHITECTURE["sections"]["right_tools_security"]["components"].items():
        md.append(f"### {cat.replace('_', ' ').title()}")
        md.append(", ".join([f"`{t}`" for t in tools]))
        md.append("")
    
    md.extend([
        "## 💡 หลักการออกแบบสำคัญ",
    ])
    
    for kp in ARCHITECTURE["key_principles"]:
        md.append(f"- {kp}")
    
    return "\n".join(md)

if __name__ == "__main__":
    output = generate_markdown()
    print(output)
