"""Credential scanning.

Patterns come from the policy, so adding a provider means a policy edit rather
than a code change. Matches report file and line, and the matched value is
redacted before it is ever formatted into a message.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .policy import Policy, read_text

# Paths where a "credential" match is documentation, not a leak.
DOC_PATH_HINTS = ("readme", "docs/", "example", "sample", "template", "test", ".md")


@dataclass
class SecretFinding:
    pattern_id: str
    description: str
    location: str
    redacted: str = ""

    def __str__(self) -> str:
        return f"{self.pattern_id} at {self.location}: {self.description}"


def redact(value: str, keep: int = 4) -> str:
    """Never echo a secret. Show a short prefix and the length."""
    text = value.strip()
    if len(text) <= keep:
        return "*" * len(text)
    return f"{text[:keep]}{'*' * max(4, len(text) - keep)}"


def _is_doc_path(rel: str) -> bool:
    lower = rel.lower()
    return any(hint in lower for hint in DOC_PATH_HINTS)


def scan_forbidden_patterns(policy: Policy, root: Path) -> list[SecretFinding]:
    """Apply every forbidden pattern from the policy across scoped files."""
    rules = policy.rule("security")
    entries = rules.get("forbidden_patterns") or []
    compiled = []
    for entry in entries:
        try:
            compiled.append(
                (entry["id"], entry.get("description", ""), re.compile(entry["pattern"]))
            )
        except (KeyError, re.error):
            # A bad pattern is a policy error, reported by validate_policy.
            continue

    findings: list[SecretFinding] = []
    for rel, path in policy.all_files(root):
        text = read_text(path)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pid, description, regex in compiled:
                match = regex.search(line)
                if not match:
                    continue
                # A credential named in prose is a false positive worth skipping,
                # but an actual key literal in a docs file is still worth flagging.
                if _is_doc_path(rel) and pid == "hardcoded_password":
                    continue
                findings.append(
                    SecretFinding(
                        pattern_id=pid,
                        description=description,
                        location=f"{rel}:{lineno}",
                        redacted=redact(match.group(0)),
                    )
                )
    return findings


def scan_committed_env(policy: Policy, root: Path) -> list[str]:
    """Return committed env files that are not on the documentation allowlist."""
    rules = policy.rule("security")
    if not rules.get("forbid_committed_env", False):
        return []

    allow = {str(a).lstrip("./") for a in (rules.get("env_allowlist") or [])}
    flagged: list[str] = []

    for rel, _path in policy.all_files(root):
        name = Path(rel).name
        if name not in (rules.get("env_files") or [".env"]):
            continue
        if name in allow:
            continue
        # Only count it if it has content that looks like an assignment.
        text = read_text(Path(root) / rel)
        if text and any(line.strip() and not line.strip().startswith("#") for line in text.splitlines()):
            flagged.append(rel)
    return flagged


def check_security(policy: Policy, root: Path) -> list[str]:
    """Combine both checks into a flat, printable finding list."""
    messages = [str(f) for f in scan_forbidden_patterns(policy, root)]
    for rel in scan_committed_env(policy, root):
        messages.append(f"env.committed at {rel}: environment file must not be committed")
    return messages
