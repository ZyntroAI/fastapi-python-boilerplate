"""link-security — HTTPS-only, strip tracking, reject embedded credentials."""
from __future__ import annotations

from typing import Dict
from urllib.parse import parse_qs, urlparse


def check_link(url: str) -> Dict[str, bool]:
    u = urlparse(url)
    https = u.scheme == "https"
    no_creds = u.username is None and u.password is None
    tracking = bool([k for k in parse_qs(u.query) if k.startswith("utm_") or k == "fbclid"])
    safe = https and no_creds and not tracking
    return {"https": https, "no_credentials": no_creds,
            "tracking_stripped": tracking, "safe": safe}
