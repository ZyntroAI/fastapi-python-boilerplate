"""Policy and manifest loading."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# loader.py lives at <suite>/src/patchsuite/loader.py
#   parents[0] = patchsuite   parents[1] = src   parents[2] = <suite>
PACKAGE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[4]


@dataclass
class Policy:
    name: str
    version: str
    raw: dict[str, Any] = field(default_factory=dict)
    source: str = ""

    @property
    def appends(self) -> dict[str, Any]:
        return self.raw.get("appends", {})

    @property
    def guard(self) -> dict[str, Any]:
        return self.raw.get("guard", {})

    @property
    def workflow(self) -> dict[str, Any]:
        return self.raw.get("workflow", {})

    @property
    def patch(self) -> dict[str, Any]:
        return self.raw.get("patch", {})

    def flag(self, section: str, key: str, default: Any = None) -> Any:
        return self.raw.get(section, {}).get(key, default)

    def as_dict(self) -> dict[str, Any]:
        return dict(self.raw)


def load_yaml(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load_policy(path: str | Path | None = None) -> Policy:
    p = Path(path) if path else PACKAGE_ROOT / "kernel" / "policy.yaml"
    raw = load_yaml(p)
    return Policy(
        name=raw.get("name", "cross-repo-patch-suite"),
        version=str(raw.get("version", "0.0.0")),
        raw=raw,
        source=str(p),
    )


def load_manifest(path: str | Path | None = None) -> dict[str, Any]:
    p = Path(path) if path else PACKAGE_ROOT / "manifest.json"
    if not p.exists():
        return {}
    import json

    return json.loads(p.read_text(encoding="utf-8"))
