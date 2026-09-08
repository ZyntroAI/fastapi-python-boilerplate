"""SSRF protection — block private/local/metadata hosts and non-HTTPS."""
from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

BLOCKED_HOSTS = {"localhost", "127.0.0.1", "::1", "metadata.google.internal", "metadata"}
BLOCKED_SCHEMES = {"file", "data", "ftp", "gopher"}


def _is_private(host: str) -> bool:
    # Resolve literal IPs; non-literal hostnames that aren't in BLOCKED are
    # checked at the resolver/firewall layer (we do not do DNS here).
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return host in BLOCKED_HOSTS
    return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved


def check(url: str) -> None:
    u = urlparse(url)
    if u.scheme != "https":
        raise ValueError(f"Fetching: HTTPS only (got {u.scheme!r})")
    if u.scheme in BLOCKED_SCHEMES:
        raise PermissionError(f"Fetching: blocked scheme {u.scheme!r}")
    host = (u.hostname or "").lower()
    if host in BLOCKED_HOSTS:
        raise PermissionError(f"Fetching: blocked host {host!r} (SSRF)")
    if _is_private(host):
        raise PermissionError(f"Fetching: private/link-local host {host!r} (SSRF)")
