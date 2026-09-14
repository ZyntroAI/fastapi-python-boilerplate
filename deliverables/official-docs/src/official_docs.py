"""Official documentation registry — Python twin of src/official-docs.js.

Same detection and safety logic as the JavaScript/TypeScript versions, adapted
to the backend's I/O model: the registry is loaded from the generated
official-docs.json (exported by scripts/export_registry.mjs) rather than
imported as a module graph, and the "which source?" question is answered from
ASGI request headers instead of DOM attributes.

Standard library only.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlsplit

DEFAULT_REGISTRY = Path(__file__).with_name("official-docs.json")

IMAGE_EXTENSIONS = frozenset({"png", "jpg", "jpeg", "webp", "gif", "svg", "avif"})

SOURCE_KEYS: dict[str, str] = {
    "FastAPI": "fastapi",
    "Python": "python",
    "FIG": "fig",
    "Dola": "dola",
    "ZyntroAI": "zyntroai",
}

__all__ = [
    "DocRegistry",
    "detect_source",
    "source_from_headers",
    "is_safe_url",
    "analyze",
    "load_registry",
]


def is_safe_url(url: str | None) -> bool:
    """Accept only http/https. Mirrors ``isSafeUrl()``."""
    if not url:
        return False
    try:
        parts = urlsplit(str(url))
    except ValueError:
        return False
    return parts.scheme in ("http", "https") and bool(parts.netloc)


def _host_and_path(raw: str) -> tuple[str, str]:
    try:
        parts = urlsplit(raw)
    except ValueError:
        return "", ""
    return parts.hostname or "", parts.path.lower()


def detect_source(src: str | None) -> str:
    """Map an asset URL to the provider it came from.

    Falls back to string sniffing when the value is not a parseable URL —
    identical behaviour to the JS implementation.
    """
    raw = "" if src is None else str(src)
    if not raw:
        return "Generic"

    host, path = _host_and_path(raw)
    if not host:
        lower = raw.lower()
        if "dola.ai" in lower:
            return "Dola"
        if "hellofig" in lower:
            return "FIG"
        if "fastapi" in lower:
            return "FastAPI"
        if "python.org" in lower:
            return "Python"
        if "zyntroai" in lower:
            return "ZyntroAI"
        return "Generic"

    if host == "dola.ai" or host.endswith(".dola.ai"):
        return "Dola"
    if host in ("hellofig.app", "hellofig.ai") or host.endswith(".hellofig.app"):
        return "FIG"
    if host == "docs.python.org" or host.endswith(".python.org"):
        return "Python"
    if host == "fastapi.tiangolo.com":
        return "FastAPI"
    if host == "github.com":
        if path.startswith("/tiangolo/fastapi"):
            return "FastAPI"
        if path.startswith("/zyntroai/"):
            return "ZyntroAI"
    return "Generic"


def source_from_headers(headers: Mapping[str, str]) -> str:
    """Backend adaptation of ``sourceFromElement()``.

    The browser reads a ``data-source`` attribute off the image element; an
    ASGI request has no DOM, so the equivalent declaration travels as the
    ``x-asset-source`` header and the fallback is ``Referer``.
    """
    lower = {str(k).lower(): str(v) for k, v in headers.items()}

    declared = lower.get("x-asset-source", "").strip()
    if declared:
        return declared

    referer = lower.get("referer") or lower.get("referrer") or ""
    if referer:
        return detect_source(referer)

    origin = lower.get("origin", "").strip()
    if origin:
        return detect_source(origin)

    return "Generic"


def analyze(src: str | None, *, alt: str = "", source: str | None = None) -> dict[str, Any]:
    """Describe an image asset: provider, official doc, structural facts.

    Mirrors the JavaScript ``analyze()`` result shape.
    """
    raw = "" if src is None else str(src)
    resolved = source or detect_source(raw)

    if is_safe_url(raw):
        parts = urlsplit(raw)
        host = parts.hostname or ""
        pathname = parts.path
    else:
        host, pathname = "", raw

    ext = ""
    for candidate in (pathname.lower(), raw.lower()):
        if "." in candidate:
            tail = candidate.rsplit(".", 1)[-1]
            tail = tail.split("#", 1)[0].split("?", 1)[0]
            if tail.isalnum():
                ext = tail
                break

    return {
        "src": raw,
        "source": resolved,
        "doc_key": SOURCE_KEYS.get(resolved),
        "host": host,
        "pathname": pathname,
        "ext": ext,
        "is_image": ext in IMAGE_EXTENSIONS,
        "is_external": raw.lower().startswith(("http://", "https://")),
        "safe": is_safe_url(raw),
        "alt": alt,
    }


class DocRegistry:
    """Loaded registry. Same knowledge as OFFICIAL_DOCS in the JS module."""

    def __init__(self, payload: Mapping[str, Any]) -> None:
        self.version: str = str(payload.get("version", ""))
        self.verified_on: str = str(payload.get("verifiedOn", ""))
        self.docs: dict[str, Any] = dict(payload.get("docs", {}))
        self.source_keys: dict[str, str] = dict(payload.get("sourceKeys", SOURCE_KEYS))
        self.corrections: list[dict[str, Any]] = list(payload.get("corrections", []))

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return f"DocRegistry(version={self.version!r}, groups={len(self.docs)})"

    def primary_url(self, key: str) -> str | None:
        entry = self.docs.get(key) or {}
        links = entry.get("links") or []
        if not links:
            return None
        url = links[0].get("url")
        return url if is_safe_url(url) else None

    def doc_for_source(self, source: str) -> dict[str, Any] | None:
        key = self.source_keys.get(source)
        return self.docs.get(key) if key else None

    def iter_links(self) -> Iterable[tuple[str, str, str, str]]:
        """Yield (group_key, group_name, link_label, url) for every link."""
        for group_key, entry in self.docs.items():
            name = str(entry.get("name", group_key))
            for link in entry.get("links", []) or []:
                yield group_key, name, str(link.get("label", "")), str(link.get("url", ""))

    def analyze(self, src: str | None, *, alt: str = "", source: str | None = None) -> dict[str, Any]:
        result = analyze(src, alt=alt, source=source)
        doc = self.doc_for_source(result["source"])
        if doc:
            key = self.source_keys[result["source"]]
            result["doc_ref"] = self.primary_url(key)
            result["doc_name"] = doc.get("name")
        return result


def load_registry(path: str | os.PathLike[str] | None = None) -> DocRegistry:
    """Load the generated registry JSON.

    Raises FileNotFoundError with an actionable message when the JSON has not
    been exported yet — run ``scripts/export_registry.mjs`` first.
    """
    target = Path(path) if path else DEFAULT_REGISTRY
    if not target.exists():
        raise FileNotFoundError(
            f"{target} not found — run `node scripts/export_registry.mjs` "
            "to export it from src/official-docs.js"
        )
    with target.open("r", encoding="utf-8") as handle:
        return DocRegistry(json.load(handle))
