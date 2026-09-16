"""dev-helpers — four small tools for the friction points in automated GitHub work.

Each module is pure stdlib and answers one question the agent currently learns
the hard way:

* :mod:`perm_checker`  — will this push be accepted, before I try it?
* :mod:`ci_workflow`   — which workflows are unpinned or silently not parsing?
* :mod:`approval_doc`  — write the request that unblocks a permission wall.
* :mod:`pr_helper`     — build a PR body whose DoD gaps are visible.

Import the flat names::

    from dev_helpers import check_push, scan_workflows, build_pr_body
"""

from __future__ import annotations

from .perm_checker import (
    check as check_push,
    explain as explain_push,
    format_report,
    normalize_path,
    required_permissions,
)
from .ci_workflow import (
    is_pinned,
    parse_state,
    scan_pins,
    scan_workflows,
)
from .approval_doc import build_approval_doc, render_markdown
from .pr_helper import DEFAULT_DOD, build_pr_body, checklist

__version__ = "1.0.0"

__all__ = [
    "__version__",
    # perm_checker
    "check_push",
    "explain_push",
    "format_report",
    "normalize_path",
    "required_permissions",
    # ci_workflow
    "is_pinned",
    "parse_state",
    "scan_pins",
    "scan_workflows",
    # approval_doc
    "build_approval_doc",
    "render_markdown",
    # pr_helper
    "DEFAULT_DOD",
    "build_pr_body",
    "checklist",
]
