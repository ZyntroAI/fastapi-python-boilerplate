import re

def check_indentation(text: str) -> dict:
    lines = text.split("\n")
    issues = []
    for i, line in enumerate(lines, 1):
        if line.strip() and len(line) - len(line.lstrip(" ")) % 2 != 0:
            issues.append(f"Line {i}: odd indentation (expected 2 spaces)")
    return {"ok": len(issues) == 0, "issues": issues}
