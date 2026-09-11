"""Obsidian Local REST API client + models (CWE-1321-hardened boundary)."""
from .client import (
    ObsidianClient,
    ObsidianError,
    NoteJson,
    build_patch_instruction,
)

__all__ = [
    "ObsidianClient",
    "ObsidianError",
    "NoteJson",
    "build_patch_instruction",
]
