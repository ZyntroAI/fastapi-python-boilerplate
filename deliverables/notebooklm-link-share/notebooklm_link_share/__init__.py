"""NotebookLM Link & Sharing Mastery.

Normalize private/artifact NotebookLM links to a clean public notebook URL,
validate UUID structure, and generate share-ready templates (short/detailed/
formal). Pure standard library — no dependencies, no credentials.

Example:
    from notebooklm_link_share import normalize_link
    clean = normalize_link("https://notebooklm.google.com/notebook/UUID/artifact/SUB?utm_source=x")
    print(clean)  # https://notebooklm.google.com/notebook/UUID
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

HOST = "notebooklm.google.com"
PATH_RE = re.compile(r"^/notebook/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?:/|$)")
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


class NotebookLMError(ValueError):
    """Raised for URLs that are not valid NotebookLM notebook links."""


def normalize_link(raw_url: str) -> str:
    """Return the clean public notebook URL from a raw/artifact/tracked link.

    Accepts http(s):// with or without scheme, with or without ``/artifact/...``
    and ``?utm_*`` / fragment params. Extracts the primary notebook UUID and
    rebuilds ``https://notebooklm.google.com/notebook/{UUID}``.
    """
    url = raw_url.strip()
    # tolerate missing scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    # strip fragment and query
    base = url.split("#", 1)[0].split("?", 1)[0]
    parsed = base.replace("https://", "").replace("http://", "")
    # only allow the known host
    if parsed != HOST and not parsed.startswith(HOST + "/"):
        raise NotebookLMError(f"not a NotebookLM notebook URL: {raw_url!r}")
    m = PATH_RE.match(parsed[len(HOST):] if parsed.startswith(HOST) else parsed)
    if not m:
        raise NotebookLMError(f"no notebook UUID found in: {raw_url!r}")
    return f"https://{HOST}/notebook/{m.group(1)}"


def normalize_skill(raw_url: str) -> Dict[str, Any]:
    """normalize_link with a structured return (mirrors the spec's helper)."""
    return {"clean_url": normalize_link(raw_url)}


def is_valid_uuid(uuid: str) -> bool:
    return bool(UUID_RE.match(uuid))


# --- share templates ---
def _title(clean_url: str) -> str:
    # title from UUID tail for a stable placeholder; callers may override
    return clean_url.rsplit("/", 1)[-1][:8]


def generate_share_text(clean_url: str, style: str = "short",
                        title: str = "", contact: str = "") -> str:
    """Generate a share message in the requested style."""
    t = title or _title(clean_url)
    if style == "short":
        return f"NotebookLM: {t}\n{clean_url}\nNo login required | View-only"
    if style == "detailed":
        contact = contact or "[Contact]"
        return (f"Shared Document - NotebookLM\n"
                f"* Title: {t}\n"
                f"* Link: {clean_url}\n"
                f"* Access: Public (Anyone with link)\n"
                f"* Permissions: Read-only\n"
                f"* Support: Report issues to {contact}")
    if style == "formal":
        return (f"Reference Document | NotebookLM\n"
                f"Access URL:\n{clean_url}\n"
                f"Classification: Publicly Accessible\n"
                f"Privilege: View-Only\n"
                f"Authentication: Not Required")
    raise NotebookLMError(f"unknown style: {style!r}")


# --- validation ---
def validate_link(clean_url: str) -> Dict[str, Any]:
    """Run the validation checklist against a URL."""
    checks: List[str] = []
    ok = True
    if clean_url.startswith(f"https://{HOST}/notebook/"):
        checks.append("structure: notebooklm.google.com/notebook/UUID")
    else:
        ok = False
        checks.append("structure: INVALID host/path")
    if "/artifact/" not in clean_url and "?" not in clean_url:
        checks.append("clean: no /artifact/ or query params")
    else:
        ok = False
        checks.append("clean: contains /artifact/ or params")
    return {
        "valid": ok,
        "checks": checks,
        "recommendation": "Share ready" if ok else "Fix before sharing",
    }


def public_skill(raw_url: str, style: str = "short",
                 title: str = "", contact: str = "") -> Dict[str, Any]:
    """Full pipeline: normalize -> validate -> generate share text."""
    clean = normalize_link(raw_url)
    validation = validate_link(clean)
    return {
        "clean_url": clean,
        "validation": validation,
        "share_template": generate_share_text(clean, style, title, contact),
    }
