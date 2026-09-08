import re

PATTERNS = [
    r"ghp_[A-Za-z0-9]{36}",
    r"gho_[A-Za-z0-9]{36}",
    r"ghs_[A-Za-z0-9]{36}",
    r"ghr_[A-Za-z0-9]{36}",
    r"github_pat_[A-Za-z0-9_]+"
]

def find_hardcoded_secrets(text: str) -> list:
    found = []
    for p in PATTERNS:
        if re.search(p, text):
            found.append(p)
    return found
