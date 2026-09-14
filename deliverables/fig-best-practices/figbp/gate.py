"""The eight gate criteria.

Each criterion returns a pass/fail plus the evidence behind it. Criteria read
their configuration from the policy; this module decides only *how* to check,
never *what* the standard says.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from . import integrations, secrets, tokens
from .policy import Policy, read_text

IMAGE_EXTENSIONS = frozenset(
    {"png", "jpg", "jpeg", "gif", "webp", "avif", "bmp", "tiff", "svg"}
)
LARGE_FILE_BYTES = 512 * 1024  # images above this are checked for format, not size


@dataclass
class CriterionResult:
    id: str
    layer: str
    severity: str
    passed: bool
    summary: str
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "layer": self.layer,
            "severity": self.severity,
            "status": "pass" if self.passed else "fail",
            "summary": self.summary,
            "evidence": self.evidence,
        }


@dataclass
class GateReport:
    root: str
    policy_version: str
    results: list[CriterionResult]

    @property
    def blocking_failures(self) -> list[CriterionResult]:
        return [r for r in self.results if not r.passed and r.severity == "blocking"]

    @property
    def advisories(self) -> list[CriterionResult]:
        return [r for r in self.results if not r.passed and r.severity != "blocking"]

    @property
    def passed(self) -> bool:
        return not self.blocking_failures

    @property
    def score(self) -> str:
        total = len(self.results) or 1
        return f"{sum(1 for r in self.results if r.passed)}/{total}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": self.root,
            "policyVersion": self.policy_version,
            "passed": self.passed,
            "score": self.score,
            "results": [r.to_dict() for r in self.results],
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _present(policy: Policy, root: Path, *names: str) -> list[str]:
    return [n for n in names if (Path(root) / n).exists()]


def _image_files(policy: Policy, root: Path) -> list[tuple[str, Path]]:
    out: list[tuple[str, Path]] = []
    for rel, path in policy.all_files(root):
        ext = rel.rsplit(".", 1)[-1].lower() if "." in rel else ""
        if ext in IMAGE_EXTENSIONS:
            out.append((rel, path))
    return out


def _ext(rel: str) -> str:
    return rel.rsplit(".", 1)[-1].lower() if "." in rel else ""


# ---------------------------------------------------------------------------
# Criteria
# ---------------------------------------------------------------------------
def check_structure(policy: Policy, root: Path) -> CriterionResult:
    rules = policy.rule("structure")
    missing: list[str] = []

    if rules.get("require_readme", True) and not (Path(root) / "README.md").exists():
        missing.append("README.md")
    if rules.get("require_standard_doc", True) and not (Path(root) / "BEST-PRACTICES.md").exists():
        missing.append("BEST-PRACTICES.md")

    for directory in rules.get("required_dirs") or []:
        if not (Path(root) / directory).is_dir():
            missing.append(f"{directory}/ (directory)")

    for name in rules.get("forbidden_root_files") or []:
        if (Path(root) / name).exists():
            missing.append(f"{name} (present but forbidden at root)")

    return CriterionResult(
        id="STRUCTURE",
        layer=rules.get("layer", "01-structure"),
        severity="blocking",
        passed=not missing,
        summary="layout complete" if not missing else f"{len(missing)} required path(s) missing",
        evidence=missing,
    )


def check_design(policy: Policy, root: Path) -> CriterionResult:
    rules = policy.rule("design")
    issues: list[str] = []
    issues.extend(str(i) for i in tokens.check_tokens(policy, root))
    issues.extend(str(i) for i in tokens.check_inline_colors(policy, root))

    return CriterionResult(
        id="DESIGN",
        layer=rules.get("layer", "02-design"),
        severity="blocking",
        passed=not issues,
        summary="tokens valid and contrast at or above floor" if not issues else f"{len(issues)} design issue(s)",
        evidence=issues,
    )


def check_security(policy: Policy, root: Path) -> CriterionResult:
    rules = policy.rule("security")

    issues = secrets.check_security(policy, root)
    # Integration contracts are a credential-handling surface: an inlined secret
    # in a contract is as much a leak as one in source, so it belongs here.
    issues.extend(integrations.check_integrations(policy, root))
    issues.extend(integrations.check_integration_egress(policy, root))

    return CriterionResult(
        id="SECURITY",
        layer=rules.get("layer", "03-security"),
        severity="blocking",
        passed=not issues,
        summary="no forbidden patterns, no committed env" if not issues else f"{len(issues)} security finding(s)",
        evidence=issues,
    )


def check_performance(policy: Policy, root: Path) -> CriterionResult:
    rules = policy.rule("performance")
    budget = int(rules.get("image_size_budget_kb", 250)) * 1024
    legacy_budget = int(rules.get("legacy_format_size_budget_kb", 60)) * 1024
    legacy = {str(f).lower() for f in (rules.get("legacy_image_formats") or [])}

    issues: list[str] = []
    for rel, path in _image_files(policy, root):
        try:
            size = path.stat().st_size
        except OSError:
            continue
        ext = _ext(rel)
        if size > budget:
            issues.append(f"{rel}: {size // 1024}KB exceeds the {budget // 1024}KB image budget")
        elif ext in legacy and size > legacy_budget:
            issues.append(
                f"{rel}: {size // 1024}KB legacy format ({ext}) above the "
                f"{legacy_budget // 1024}KB allowance — convert to a modern format"
            )

    return CriterionResult(
        id="PERFORMANCE",
        layer=rules.get("layer", "04-performance"),
        severity="blocking",
        passed=not issues,
        summary="images within budget" if not issues else f"{len(issues)} asset(s) over budget",
        evidence=issues,
    )


def check_testing(policy: Policy, root: Path) -> CriterionResult:
    rules = policy.rule("testing")
    from .policy import matches_any

    if not rules.get("require_tests", True):
        return CriterionResult("TESTING", rules.get("layer", "05-team"), "blocking", True, "not required")

    globs = list(rules.get("test_file_globs") or [])
    dirs = {str(d) for d in (rules.get("test_dir_names") or [])}

    found: list[str] = []
    for rel, _path in policy.all_files(root):
        if matches_any(rel, globs) or set(rel.split("/")) & dirs:
            found.append(rel)

    return CriterionResult(
        id="TESTING",
        layer=rules.get("layer", "05-team"),
        severity="blocking",
        passed=bool(found),
        summary=f"{len(found)} test file(s)" if found else "no test files found",
        evidence=found[:10],
    )


def check_permissions(policy: Policy, root: Path) -> CriterionResult:
    """Every declared role must exist, and every agent file must carry a scope."""
    rules = policy.rule("permissions")
    if not rules.get("require_declared_roles", True):
        return CriterionResult("PERMISSIONS", rules.get("layer", "05-team"), "blocking", True, "not required")

    issues: list[str] = []
    layer_ids = {layer.get("id") for layer in policy.layers}
    declared_roles = set(policy.roles)

    # Every layer's owner must be a real role.
    for layer in policy.layers:
        owner = layer.get("owner_role")
        if owner and owner not in declared_roles:
            issues.append(f"layer {layer['id']}: owner {owner!r} is not a declared role")

    # Every role's scope must be a real layer.
    for role, entry in policy.roles.items():
        scope = entry.get("scope") if isinstance(entry, dict) else None
        if scope and scope not in layer_ids:
            issues.append(f"role {role}: scope {scope!r} is not a declared layer")

    # An agent instruction file must declare a scope that exists.
    agents_dir = Path(root) / "agents"
    if agents_dir.is_dir():
        for path in sorted(agents_dir.glob("*.md")):
            if path.name.upper() == "README.MD":
                continue
            text = read_text(path) or ""
            match = re.search(
                r"(?im)^\s*(?:\*\*)?scope(?:\*\*)?\s*[:=]\s*\*{0,2}\s*`?([0-9]{2}-[a-z-]+)`?",
                text,
            )
            rel = path.relative_to(root).as_posix()
            if not match:
                issues.append(f"{rel}: no 'scope:' declaration found")
            elif match.group(1) not in layer_ids:
                issues.append(f"{rel}: scope {match.group(1)!r} is not a declared layer")

    return CriterionResult(
        id="PERMISSIONS",
        layer=rules.get("layer", "05-team"),
        severity="blocking",
        passed=not issues,
        summary="roles and agent scopes consistent" if not issues else f"{len(issues)} permission issue(s)",
        evidence=issues,
    )


def check_backup(policy: Policy, root: Path) -> CriterionResult:
    rules = policy.rule("backup")
    issues: list[str] = []

    if rules.get("require_backup_record", True):
        if not _present(policy, root, *[str(f) for f in (rules.get("record_files") or ["BACKUP.md"])]):
            issues.append(
                "no backup record found (expected one of: "
                + ", ".join(str(f) for f in (rules.get("record_files") or ["BACKUP.md"]))
                + ")"
            )
    if rules.get("require_rollback_path", True):
        candidates = [str(f) for f in (rules.get("record_files") or [])]
        rollback = [c for c in candidates if "rollback" in c.lower()]
        text_present = False
        for candidate in candidates:
            path = Path(root) / candidate
            if path.exists():
                body = (read_text(path) or "").lower()
                if "rollback" in body:
                    text_present = True
                    break
        if not rollback and not text_present:
            issues.append("no rollback path recorded")

    return CriterionResult(
        id="BACKUP",
        layer=rules.get("layer", "06-deployment"),
        severity="blocking",
        passed=not issues,
        summary="backup and rollback recorded" if not issues else f"{len(issues)} backup gap(s)",
        evidence=issues,
    )


def check_deployment(policy: Policy, root: Path) -> CriterionResult:
    rules = policy.rule("deployment")
    issues: list[str] = []

    if rules.get("require_approval_record", True):
        if not _present(policy, root, *[str(f) for f in (rules.get("approval_files") or ["DEPLOYMENT.md"])]):
            issues.append(
                "no approval record (expected one of: "
                + ", ".join(str(f) for f in (rules.get("approval_files") or ["DEPLOYMENT.md"]))
                + ")"
            )

    for artifact in rules.get("required_artifacts") or []:
        if not (Path(root) / str(artifact)).exists():
            issues.append(f"required artifact missing: {artifact}")

    # Supply-chain: a workflow using a floating action tag fails deployment.
    supply = policy.supply_chain
    if supply.get("actions_must_be_sha_pinned", False):
        workflow_dirs = [Path(root) / ".github" / "workflows"]
        for wf_dir in workflow_dirs:
            if not wf_dir.is_dir():
                continue
            for wf in sorted(wf_dir.glob("*.y*ml")):
                text = read_text(wf) or ""
                for lineno, line in enumerate(text.splitlines(), start=1):
                    if "uses:" not in line:
                        continue
                    ref = line.split("uses:", 1)[1].strip().split()[0] if line.split("uses:", 1)[1].strip() else ""
                    if "@" not in ref:
                        continue
                    version = ref.rsplit("@", 1)[1]
                    if not re.fullmatch(r"[0-9a-f]{40}", version):
                        rel = wf.relative_to(root).as_posix()
                        issues.append(f"{rel}:{lineno}: action {ref} is not SHA-pinned")

    return CriterionResult(
        id="DEPLOYMENT",
        layer=rules.get("layer", "06-deployment"),
        severity="blocking",
        passed=not issues,
        summary="release evidence complete" if not issues else f"{len(issues)} deployment gap(s)",
        evidence=issues,
    )


CRITERIA: dict[str, Callable[[Policy, Path], CriterionResult]] = {
    "STRUCTURE": check_structure,
    "DESIGN": check_design,
    "SECURITY": check_security,
    "PERFORMANCE": check_performance,
    "TESTING": check_testing,
    "PERMISSIONS": check_permissions,
    "BACKUP": check_backup,
    "DEPLOYMENT": check_deployment,
}


def run_gate(policy: Policy, root: str | Path) -> GateReport:
    """Evaluate every criterion the policy declares, in policy order."""
    root_path = Path(root).resolve()
    results: list[CriterionResult] = []

    for criterion in policy.criteria:
        cid = str(criterion.get("id", "")).upper()
        check = CRITERIA.get(cid)
        if check is None:
            results.append(
                CriterionResult(
                    id=cid or "UNKNOWN",
                    layer=str(criterion.get("layer", "")),
                    severity=str(criterion.get("severity", "blocking")),
                    passed=True,
                    summary="no implementation — criterion declared but not checked",
                    evidence=[f"policy declares {cid!r} but figbp/gate.py has no check for it"],
                )
            )
            continue
        result = check(policy, root_path)
        # Policy is authoritative on severity and layer.
        result.severity = str(criterion.get("severity", result.severity))
        result.layer = str(criterion.get("layer", result.layer))
        results.append(result)

    return GateReport(
        root=str(root_path),
        policy_version=policy.version,
        results=results,
    )
