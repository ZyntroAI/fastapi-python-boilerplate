"""Client for the Obsidian Local REST API (v3.x).

Covers the documented endpoint surface:

  GET    /                       API version + auth check
  GET    /vault/                 list vault root
  GET    /vault/{path}/          list a directory
  GET    /vault/{file}           read a note (markdown | vnd.olrapi.note+json | document-map)
  PUT    /vault/{file}           create / replace a note
  POST   /vault/{file}           append to a note (or a targeted section)
  PATCH  /vault/{file}           structured patch instruction
  DELETE /vault/{file}           delete a note
  GET    /active/                read the active note
  POST   /search/                JsonLogic search over the vault
  POST   /search/simple/         plain full-text search
  GET    /tags/                  all tags
  GET    /commands/              list registered commands
  POST   /commands/{id}/         execute a command
  POST   /open/{file}            open a file in the Obsidian UI

Transport is injectable (``transport=callable``) so the whole surface is
testable without a live vault, and no third-party HTTP dependency is added.

Untrusted input (query params, headings, filenames) is validated before it
reaches the API: path traversal is rejected and JSON payloads are copied
through the CWE-1321 sanitizer, since path/query data is exactly the
prototype-pollution boundary the suite guards.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ..cwe1321_bridge import sanitize_prototype_keys

# Content types the API negotiates on.
ACCEPT_MARKDOWN = "text/markdown"
ACCEPT_NOTE_JSON = "application/vnd.olrapi.note+json"
ACCEPT_DOCUMENT_MAP = "application/vnd.olrapi.document-map+json"
ACCEPT_HTML = "text/html"
CONTENT_JSONLOGIC = "application/vnd.olrapi.jsonlogic+json"
CONTENT_PATCH_INSTRUCTION = "application/vnd.olrapi.patch-instruction+json"

DEFAULT_HTTP_PORT = 27123
DEFAULT_HTTPS_PORT = 27124
API_VERSION_HEADER = "Markdown-Patch-Version"

HEADING, BLOCK, FRONTMATTER = "heading", "block", "frontmatter"
REPLACE, PREPEND, APPEND, DELETE = "replace", "prepend", "append", "delete"


class ObsidianError(RuntimeError):
    """Raised for any non-2xx response or transport failure."""

    def __init__(self, status: int, message: str, body: Any = None) -> None:
        super().__init__(f"Obsidian API {status}: {message}")
        self.status = status
        self.message = message
        self.body = body


@dataclass
class Response:
    """Normalised API response."""

    status: int
    headers: Dict[str, str] = field(default_factory=dict)
    text: str = ""
    raw: bytes = b""

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    def json(self) -> Any:
        return json.loads(self.text or "null")


@dataclass
class NoteJson:
    """Parsed form of ``Accept: application/vnd.olrapi.note+json``."""

    content: str = ""
    frontmatter: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    path: str = ""
    stat: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "NoteJson":
        payload = sanitize_prototype_keys(payload or {})
        return cls(
            content=payload.get("content", "") or "",
            frontmatter=payload.get("frontmatter") or {},
            tags=payload.get("tags") or [],
            path=payload.get("path", "") or "",
            stat=payload.get("stat") or {},
        )


# --------------------------------------------------------------------------- #
# Validation helpers — the untrusted-input boundary
# --------------------------------------------------------------------------- #

def _validate_name(name: str, *, label: str = "path") -> str:
    """Reject traversal / absolute paths; normalise separators.

    The API addresses notes by *vault-relative* path, so any ``..`` segment,
    leading slash, or NUL is refused before the request is built.
    """
    if not isinstance(name, str) or not name:
        raise ValueError(f"{label} must be a non-empty string")
    if "\x00" in name:
        raise ValueError(f"{label} contains a NUL byte")
    cleaned = name.replace("\\", "/").strip("/")
    if name.startswith("/"):
        raise ValueError(f"{label} must be vault-relative, not absolute")
    parts = [p for p in cleaned.split("/") if p not in ("", ".")]
    if any(p == ".." for p in parts):
        raise ValueError(f"{label} must not contain '..' segments")
    return "/".join(parts)


def _encode_path(path: str) -> str:
    """Percent-encode each segment, preserving separators."""
    return "/".join(urllib.parse.quote(seg, safe="") for seg in path.split("/"))


def build_patch_instruction(
    target_type: str,
    target: Any,
    operation: str,
    *,
    scope: str = "content",
    content: Optional[str] = None,
    value: Any = None,
    destination: Optional[Dict[str, Any]] = None,
    within: Optional[int] = None,
    if_match: Optional[str] = None,
    create_target_if_missing: bool = False,
    reject_if_content_preexists: bool = False,
) -> Dict[str, Any]:
    """Build and validate a markdown-patch instruction.

    Enforces the documented algebra: exactly one payload carrier
    (``content`` / ``value`` / ``destination``), and the operation x scope x
    target type combinations the API accepts.
    """
    if target_type not in (HEADING, BLOCK, FRONTMATTER):
        raise ValueError(f"invalid targetType: {target_type!r}")
    if operation not in (REPLACE, PREPEND, APPEND, DELETE):
        raise ValueError(f"invalid operation: {operation!r}")
    if scope not in ("content", "marker", "markerAndContent", "parent"):
        raise ValueError(f"invalid scope: {scope!r}")

    carriers = [c for c in (content, value, destination) if c is not None]
    if scope == "parent":
        if operation != REPLACE or destination is None:
            raise ValueError("scope 'parent' requires operation 'replace' and a destination")
    elif len(carriers) != 1:
        raise ValueError("provide exactly one of content, value, or destination")
    if scope == "parent" and len(carriers) != 1:
        raise ValueError("a move carries only a destination")

    if within is not None and create_target_if_missing:
        raise ValueError("'within' cannot be combined with createTargetIfMissing")

    instruction: Dict[str, Any] = {
        "targetType": target_type,
        "target": target,
        "operation": operation,
    }
    if scope != "content":
        instruction["scope"] = scope
    if content is not None:
        instruction["content"] = content
    if value is not None:
        instruction["value"] = value
    if destination is not None:
        instruction["destination"] = destination
    if within is not None:
        instruction["within"] = within
    if if_match:
        instruction["ifMatch"] = if_match
    if create_target_if_missing:
        instruction["createTargetIfMissing"] = True
    if reject_if_content_preexists:
        instruction["rejectIfContentPreexists"] = True
    return instruction


def _default_transport(method: str, url: str, headers: Dict[str, str], body: Optional[bytes]) -> Response:
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310 (scheme checked by caller)
            raw = resp.read()
            return Response(resp.status, dict(resp.headers), raw.decode("utf-8", "replace"), raw)
    except urllib.error.HTTPError as exc:  # pragma: no cover - exercised via injected transport
        raw = exc.read()
        return Response(exc.code, dict(exc.headers or {}), raw.decode("utf-8", "replace"), raw)
    except urllib.error.URLError as exc:  # pragma: no cover
        raise ObsidianError(0, f"transport failure: {exc.reason}") from exc


class ObsidianClient:
    """Thin, typed wrapper over the Obsidian Local REST API.

    Reads are always permitted; mutations require ``allow_write=True`` so a
    read-only deployment cannot accidentally modify a vault.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        *,
        allow_write: bool = False,
        transport: Optional[Callable[[str, str, Dict[str, str], Optional[bytes]], Response]] = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required")
        parsed = urllib.parse.urlparse(base_url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("base_url must be http:// or https://")
        self.base_url = base_url.rstrip("/")
        self._api_key = api_key or ""
        self.allow_write = allow_write
        self._transport = transport or _default_transport

    # -- plumbing ---------------------------------------------------------- #

    def _request(
        self,
        method: str,
        path: str,
        *,
        accept: Optional[str] = None,
        content_type: Optional[str] = None,
        body: Any = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        url = f"{self.base_url}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        hdrs: Dict[str, str] = {"Authorization": f"Bearer {self._api_key}"}
        if accept:
            hdrs["Accept"] = accept
        raw: Optional[bytes] = None
        if body is not None:
            if isinstance(body, (dict, list)):
                body = sanitize_prototype_keys(body)
                raw = json.dumps(body).encode("utf-8")
            elif isinstance(body, str):
                raw = body.encode("utf-8")
            else:
                raw = bytes(body)
        if content_type:
            hdrs["Content-Type"] = content_type
        if headers:
            hdrs.update(headers)
        resp = self._transport(method, url, hdrs, raw)
        if not resp.ok:
            raise ObsidianError(resp.status, resp.text[:500] or "request failed", resp.raw)
        return resp

    def _write_guard(self) -> None:
        if not self.allow_write:
            raise ObsidianError(403, "client is read-only (construct with allow_write=True)")

    # -- meta -------------------------------------------------------------- #

    def api_root(self) -> Dict[str, Any]:
        """GET / — API identity and authenticated status."""
        return self._request("GET", "/", accept=ACCEPT_NOTE_JSON).json()

    def api_version(self) -> Dict[str, Any]:
        """GET / — authenticated status + service/plugin versions."""
        return self.api_root()

    # -- vault reads ------------------------------------------------------- #

    def list_vault(self) -> List[str]:
        """GET /vault/ — files at the vault root."""
        return self._request("GET", "/vault/").json()

    def list_dir(self, path: str = "") -> List[str]:
        """GET /vault/{path}/ — files in a directory."""
        if not path:
            return self._request("GET", "/vault/").json()
        clean = _validate_name(path)
        return self._request("GET", f"/vault/{_encode_path(clean)}/").json()

    def read_note(
        self,
        filename: str,
        *,
        accept: str = ACCEPT_MARKDOWN,
        target_type: Optional[str] = None,
        target: Optional[str] = None,
        target_scope: Optional[str] = None,
    ) -> str:
        """GET /vault/{file} — note body (markdown by default)."""
        clean = _validate_name(filename, label="filename")
        headers: Dict[str, str] = {}
        if target_type:
            headers["Target-Type"] = target_type
        if target:
            headers["Target"] = target
        if target_scope:
            headers["Target-Scope"] = target_scope
        return self._request(
            "GET", f"/vault/{_encode_path(clean)}", accept=accept, headers=headers
        ).text

    def read_note_json(self, filename: str) -> NoteJson:
        """GET /vault/{file} with note+json — parsed frontmatter and tags."""
        return NoteJson.from_payload(
            self._request(
                "GET",
                f"/vault/{_encode_path(_validate_name(filename, label='filename'))}",
                accept=ACCEPT_NOTE_JSON,
            ).json()
        )

    def document_map(self, filename: str) -> Dict[str, Any]:
        """GET /vault/{file} with document-map+json — heading tree + version token."""
        return self._request(
            "GET",
            f"/vault/{_encode_path(_validate_name(filename, label='filename'))}",
            accept=ACCEPT_DOCUMENT_MAP,
        ).json()

    def read_active(self) -> str:
        """GET /active/ — the note currently open in Obsidian."""
        return self._request("GET", "/active/", accept=ACCEPT_MARKDOWN).text

    def tags(self) -> Dict[str, int]:
        """GET /tags/ — tag to occurrence count."""
        return self._request("GET", "/tags/").json()

    def commands(self) -> List[Dict[str, Any]]:
        """GET /commands/ — registered Obsidian commands."""
        return self._request("GET", "/commands/").json()

    # -- search ------------------------------------------------------------ #

    def search(self, jsonlogic: Dict[str, Any]) -> List[Dict[str, Any]]:
        """POST /search/ — JsonLogic query over every note in the vault."""
        return self._request(
            "POST",
            "/search/",
            content_type=CONTENT_JSONLOGIC,
            accept=ACCEPT_NOTE_JSON,
            body=jsonlogic,
        ).json()

    def simple_search(self, query: str, *, context_length: int = 100) -> List[Dict[str, Any]]:
        """POST /search/simple/ — plain full-text search with context."""
        return self._request(
            "POST",
            "/search/simple/",
            accept=ACCEPT_NOTE_JSON,
            params={"query": query, "contextLength": context_length},
        ).json()

    # -- writes ------------------------------------------------------------ #

    def write_note(self, filename: str, content: str) -> Response:
        """PUT /vault/{file} — create or replace a note."""
        self._write_guard()
        return self._request(
            "PUT",
            f"/vault/{_encode_path(_validate_name(filename, label='filename'))}",
            content_type="text/markdown",
            body=content,
        )

    def append_note(
        self,
        filename: str,
        content: str,
        *,
        target_type: Optional[str] = None,
        target: Optional[str] = None,
    ) -> Response:
        """POST /vault/{file} — append to a note, or to a targeted section."""
        self._write_guard()
        headers = {}
        if target_type:
            headers["Target-Type"] = target_type
        if target:
            headers["Target"] = target
        return self._request(
            "POST",
            f"/vault/{_encode_path(_validate_name(filename, label='filename'))}",
            content_type="text/markdown",
            body=content,
            headers=headers,
        )

    def patch_note(self, filename: str, instruction: Dict[str, Any]) -> Response:
        """PATCH /vault/{file} — apply one structured patch instruction."""
        self._write_guard()
        return self._request(
            "PATCH",
            f"/vault/{_encode_path(_validate_name(filename, label='filename'))}",
            content_type=CONTENT_PATCH_INSTRUCTION,
            body=instruction,
        )

    def delete_note(self, filename: str, *, permanent: bool = False) -> Response:
        """DELETE /vault/{file} — trash (default) or permanently delete."""
        self._write_guard()
        return self._request(
            "DELETE",
            f"/vault/{_encode_path(_validate_name(filename, label='filename'))}",
            params={"permanent": str(permanent).lower()},
        )

    def execute_command(self, command_id: str) -> Response:
        """POST /commands/{id}/ — run an Obsidian command."""
        self._write_guard()
        return self._request("POST", f"/commands/{_encode_path(_validate_name(command_id, label='commandId'))}/")

    def open_file(self, filename: str, *, new_leaf: bool = False) -> Response:
        """POST /open/{file} — open a note in the Obsidian UI."""
        self._write_guard()
        return self._request(
            "POST",
            f"/open/{_encode_path(_validate_name(filename, label='filename'))}",
            params={"newLeaf": str(new_leaf).lower()},
        )
