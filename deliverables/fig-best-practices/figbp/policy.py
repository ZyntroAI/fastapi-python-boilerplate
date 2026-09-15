"""Policy loading, glob matching, and file walking.

Everything the gate knows about the standard comes from
``policy/fig-best-practices.yaml``. Nothing downstream hard-codes a rule, so a
new criterion is a policy edit plus a check function.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

import yaml

DEFAULT_POLICY = Path(__file__).resolve().parents[1] / "policy" / "fig-best-practices.yaml"

# Never walked, regardless of policy. These are not project source.
HARD_SKIP_DIRS = frozenset({".git", "node_modules", ".venv", "venv", "__pycache__", ".mypy_cache"})

# Reading more than this into memory for pattern scanning is pointless and risky.
MAX_SCAN_BYTES = 2 * 1024 * 1024


def glob_to_regex(glob: str) -> re.Pattern[str]:
    """Translate a glob to a regex.

    ``fnmatch`` alone is wrong here: it treats ``**/*.py`` as a single-segment
    pattern, so ``src/a/b.py`` would not match. This handles ``**`` properly.
    """
    g = str(glob).replace("\\", "/")
    out: list[str] = []
    i = 0
    while i < len(g):
        if g.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif g.startswith("**", i):
            out.append(".*")
            i += 2
        elif g[i] == "*":
            out.append("[^/]*")
            i += 1
        elif g[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(g[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def matches_any(rel_path: str, globs: Sequence[str]) -> bool:
    return any(glob_to_regex(g).match(rel_path) for g in globs)


def iter_files(
    root: Path,
    apply_to: Sequence[str] | None = None,
    exempt: Sequence[str] | None = None,
) -> Iterator[tuple[str, Path]]:
    """Yield ``(relative_posix_path, absolute_path)`` for project files.

    ``apply_to=None`` means every file (still honouring HARD_SKIP_DIRS).
    """
    root = Path(root).resolve()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        parts = set(rel.split("/"))
        if parts & HARD_SKIP_DIRS:
            continue
        if exempt and matches_any(rel, exempt):
            continue
        if apply_to and not matches_any(rel, apply_to):
            # A file that the policy does not scope is invisible to the gate,
            # but .md and config files are still needed for evidence criteria —
            # callers that need those pass apply_to=None.
            continue
        yield rel, path


def read_text(path: Path) -> str | None:
    """Read a file as text, or return None when it is binary or too large."""
    try:
        if path.stat().st_size > MAX_SCAN_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="strict")
    except (UnicodeDecodeError, OSError):
        return None


@dataclass
class Policy:
    """Parsed policy. Attribute access mirrors the YAML keys."""

    raw: Mapping[str, Any]
    path: Path
    version: str = ""
    standard: str = ""
    verified_on: str = ""
    errors: list[str] = field(default_factory=list)

    # ---- accessors -----------------------------------------------------
    def section(self, name: str) -> dict[str, Any]:
        value = self.raw.get(name)
        return dict(value) if isinstance(value, Mapping) else {}

    @property
    def layers(self) -> list[dict[str, Any]]:
        return list(self.raw.get("layers") or [])

    @property
    def roles(self) -> dict[str, Any]:
        return dict(self.raw.get("roles") or {})

    @property
    def scope(self) -> dict[str, Any]:
        return self.section("scope")

    @property
    def rules(self) -> dict[str, Any]:
        return self.section("rules")

    @property
    def criteria(self) -> list[dict[str, Any]]:
        return list(self.section("quality_gate").get("criteria") or [])

    @property
    def supply_chain(self) -> dict[str, Any]:
        return self.section("supply_chain")

    @property
    def corrections(self) -> list[dict[str, Any]]:
        return list(self.raw.get("corrections") or [])

    def rule(self, name: str) -> dict[str, Any]:
        value = self.rules.get(name)
        return dict(value) if isinstance(value, Mapping) else {}

    def role_scope(self, role: str) -> str | None:
        entry = self.roles.get(role)
        return entry.get("scope") if isinstance(entry, Mapping) else None

    def declares_role(self, name: str) -> bool:
        return name in self.roles

    def scoped_files(self, root: Path) -> Iterator[tuple[str, Path]]:
        """Files the policy applies to."""
        return iter_files(root, self.scope.get("apply_to"), self.scope.get("exempt"))

    def all_files(self, root: Path) -> Iterator[tuple[str, Path]]:
        """Every project file, ignoring apply_to but honouring exempt."""
        return iter_files(root, None, self.scope.get("exempt"))


def load_policy(path: str | Path | None = None) -> Policy:
    """Load and structurally validate the policy file."""
    target = Path(path) if path else DEFAULT_POLICY
    if not target.exists():
        raise FileNotFoundError(f"policy file not found: {target}")

    with target.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    if not isinstance(raw, Mapping):
        raise ValueError(f"policy root must be a mapping, got {type(raw).__name__}")

    policy = Policy(
        raw=raw,
        path=target,
        version=str(raw.get("version", "")),
        standard=str(raw.get("standard", "")),
        verified_on=str(raw.get("verified_on", "")),
    )
    policy.errors = validate_policy(policy)
    return policy


def validate_policy(policy: Policy) -> list[str]:
    """Structural checks — a malformed policy must fail loudly, not silently."""
    errors: list[str] = []

    if not policy.version:
        errors.append("version is required")
    if not policy.standard:
        errors.append("standard is required")

    if not policy.layers:
        errors.append("at least one layer is required")
    for layer in policy.layers:
        for key in ("id", "name", "purpose", "owner_role"):
            if not layer.get(key):
                errors.append(f"layer {layer.get('id', '?')}: missing {key}")

    layer_ids = {layer.get("id") for layer in policy.layers}
    role_names = set(policy.roles)

    for role, entry in policy.roles.items():
        if not isinstance(entry, Mapping):
            errors.append(f"role {role}: must be a mapping")
            continue
        scope = entry.get("scope")
        if not scope:
            errors.append(f"role {role}: missing scope")
        elif scope not in layer_ids:
            errors.append(f"role {role}: scope {scope!r} is not a declared layer")

    for layer in policy.layers:
        owner = layer.get("owner_role")
        if owner and owner not in role_names:
            errors.append(f"layer {layer['id']}: owner_role {owner!r} is not a declared role")

    if not policy.criteria:
        errors.append("quality_gate.criteria must not be empty")
    seen: set[str] = set()
    for criterion in policy.criteria:
        cid = criterion.get("id")
        if not cid:
            errors.append("criterion missing id")
            continue
        if cid in seen:
            errors.append(f"duplicate criterion id: {cid}")
        seen.add(cid)
        if criterion.get("severity") not in ("blocking", "advisory"):
            errors.append(f"criterion {cid}: severity must be blocking or advisory")

    design = policy.rule("design")
    floor = design.get("contrast_floor")
    if floor is not None and not (1.0 <= float(floor) <= 21.0):
        errors.append(f"design.contrast_floor out of range: {floor}")

    for entry in policy.rule("security").get("forbidden_patterns") or []:
        try:
            re.compile(entry["pattern"])
        except (KeyError, re.error) as exc:
            errors.append(f"security pattern {entry.get('id', '?')}: {exc}")

    return errors
