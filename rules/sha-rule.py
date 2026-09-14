import re

def validate_sha_pins(text: str) -> dict:
    refs = re.findall(r"uses:\s+([\w/-]+)@([a-f0-9]{40})", text)
    bad = re.findall(r"uses:\s+[\w/-]+@v[\d.]+", text)
    return {"pass": len(bad) == 0, "sha_count": len(refs), "tag_count": len(bad)}
