"""link-resolver — parse, normalize, extract ids from a NotebookLM URL."""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

HOST = "notebooklm.google.com"
UUID_RE = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
# artifact ids vary in length in the wild (e.g. trailing group of 11), so we
# accept a lenient hex-dash token there; notebook id stays strict.
_ART_RE = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{10,12}"
_NB_RE = re.compile(r"^/notebook/(" + UUID_RE + r")(?:/artifact/(" + _ART_RE + r"))?(?:/|$)")


class ResolverError(ValueError):
    pass


def parse(raw_url: str) -> Dict[str, Any]:
    """Split a URL into host, path, notebook_id, artifact_id, query params."""
    url = raw_url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    scheme, rest = url.split("://", 1)
    if scheme != "https":
        raise ResolverError("HTTPS only")
    host, _, tail = rest.partition("/")
    path, _, query = tail.partition("?")
    path = "/" + path
    return {"scheme": scheme, "host": host, "path": path,
            "query": query, "raw": raw_url}


def _ids(url: str):
    """Extract notebook_id + optional artifact_id from a canonical-path URL."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    # strip scheme+host then match path
    hostpath = url.split("://", 1)[1]
    path = "/" + hostpath.split("/", 1)[1]
    mm = _NB_RE.match(path)
    if not mm:
        raise ResolverError("no notebook UUID found")
    return {"notebook_id": mm.group(1), "artifact_id": mm.group(2)}


def normalize(raw_url: str) -> str:
    """Return the canonical notebook URL (artifact + tracking stripped)."""
    info = parse(raw_url)
    if info["host"] != HOST:
        raise ResolverError(f"not a NotebookLM URL: {info['host']}")
    ids = _ids("https://" + HOST + info["path"])
    return f"https://{HOST}/notebook/{ids['notebook_id']}"


def canonical_url(raw_url: str) -> str:
    return normalize(raw_url)


def extract_artifact(raw_url: str) -> Optional[str]:
    """Return the artifact_id if present, else None."""
    try:
        return _ids("https://" + HOST + parse(raw_url)["path"]).get("artifact_id")
    except ResolverError:
        return None


def resolve(raw_url: str) -> Dict[str, Any]:
    """Full resolve: canonical URL + ids + tracking_removed."""
    info = parse(raw_url)
    canon = normalize(raw_url)
    ids = _ids("https://" + HOST + info["path"])
    return {
        "resource": {
            "provider": "notebooklm",
            "notebook_id": ids["notebook_id"],
            "artifact_id": ids.get("artifact_id"),
            "canonical_url": canon,
            "tracking_removed": bool(info["query"]) or bool(ids.get("artifact_id")),
        }
    }
