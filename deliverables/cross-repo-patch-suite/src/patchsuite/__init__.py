"""cross-repo-patch-suite — keep patches byte-faithful across repositories.

Public surface::

    from patchsuite import append_text, verify_append, guard, audit_pins
"""

from __future__ import annotations

from .append import (
    AppendResult,
    AppendVerification,
    append_text,
    diff_stat,
    plan_append,
    safe_read,
    verify_append,
)
from .eol import (
    ByteProfile,
    detect_eol,
    dominant_terminator,
    ends_with_newline,
    normalize_terminators,
    profile,
    to_bytes,
)
from .gitops import (
    apply_mailbox,
    apply_patch,
    audit_eol_risk,
    check_patch,
    diagnose_patch_failure,
    working_tree_state,
)
from .guard import Decision, GuardResult, Intent, all_allowed, guard, plan_writes
from .loader import Policy, load_manifest, load_policy
from .yamlgate import (
    ActionRef,
    PinAudit,
    YamlCheck,
    audit_pins,
    find_action_refs,
    is_sha_pinned,
    resolve_sha,
    validate_yaml_file,
)

__version__ = "1.0.0"

__all__ = [
    "AppendResult",
    "AppendVerification",
    "ActionRef",
    "ByteProfile",
    "Decision",
    "GuardResult",
    "Intent",
    "PinAudit",
    "Policy",
    "YamlCheck",
    "all_allowed",
    "append_text",
    "audit_pins",
    "detect_eol",
    "diff_stat",
    "dominant_terminator",
    "ends_with_newline",
    "find_action_refs",
    "guard",
    "is_sha_pinned",
    "load_manifest",
    "load_policy",
    "plan_append",
    "plan_writes",
    "profile",
    "resolve_sha",
    "safe_read",
    "to_bytes",
    "validate_yaml_file",
    "verify_append",
]
