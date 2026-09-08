# 🛠️ Patch Skill — Controlled Change Management Layer
**Path:** `skills/patch/` — Minimal, auditable, reversible code changes

---

## 📁 Final Structure
```
skills/patch/
├── SKILL.md               # Documentation & API
├── __init__.py            # Export core API
├── analyze/               # Impact & context analysis
│   ├── __init__.py
│   ├── diff.py            # Parse/compare changes
│   ├── context.py         # Git/repo state
│   └── impact.py          # Risk/scope analysis
├── generate/              # Create minimal diffs
│   ├── __init__.py
│   ├── unified_diff.py    # Standard patch format
│   ├── file_patch.py      # Single-file changes
│   └── migration.py       # Multi-file/structure
├── validate/              # Safety & compliance
│   ├── __init__.py
│   ├── syntax.py          # Language syntax check
│   ├── conflict.py        # Detect merge conflicts
│   ├── tests.py           # Run existing tests
│   └── security.py        # Scan secrets/risk
├── apply/                 # Execution & rollback
│   ├── __init__.py
│   ├── apply.py           # Apply patch
│   ├── dry_run.py         # Preview without change
│   └── rollback.py        # Revert safely
└── tests/                 # Skill self-tests
    └── test_patch.py
```

---

## 🧠 Core API (`__init__.py`)
```python
"""
🛠️ Patch Skill — Controlled Change Management
Purpose: Minimal, validatable, reversible code changes
"""
from typing import Dict, List, Optional
from .analyze.diff import analyze_diff
from .analyze.impact import assess_impact
from .generate.unified_diff import create_diff
from .validate.syntax import check_syntax
from .validate.conflict import detect_conflicts
from .validate.tests import run_test_suite
from .validate.security import scan_security
from .apply.dry_run import preview_changes
from .apply.apply import execute_patch
from .apply.rollback import safe_rollback

class PatchSkill:
    """
    Mutation layer — Agents decide *what* → Patch controls *how*
    """
    def __init__(self):
        self.policy = PatchPolicy()
        self.history: List[Dict] = []

    def create(self,
               files: List[Dict],
               reason: str,
               issue: Optional[str] = None,
               target_branch: str = "main") -> Dict:
        """Build patch object — minimal diff + metadata"""
        return {
            "id": f"patch_{len(self.history):03d}",
            "type": "bugfix",
            "status": "proposed",
            "target": target_branch,
            "files": files,
            "reason": reason,
            "issue": issue,
            "risk": {"level": "unknown"},
            "validation": {},
            "rollback": {"available": False}
        }

    def generate(self, base: str, modified: str) -> str:
        """Generate unified diff"""
        return create_diff(base, modified)

    def analyze(self, patch: Dict) -> Dict:
        """Analyze risk, scope, context"""
        impact = assess_impact(patch)
        patch["risk"] = impact
        return patch

    def validate(self, patch: Dict) -> Dict:
        """Syntax + conflict + tests + security"""
        patch["validation"] = {
            "syntax": check_syntax(patch),
            "conflict": detect_conflicts(patch),
            "tests": run_test_suite(patch),
            "security": scan_security(patch)
        }
        return patch

    def preview(self, patch: Dict) -> Dict:
        """Dry run — no changes"""
        return preview_changes(patch)

    def confidence(self, patch: Dict) -> float:
        """Score: 0.0–1.0"""
        rc = patch.get("risk", {}).get("root_cause_confidence", 0.0)
        pc = 0.95 if all(v == "pass" for v in patch["validation"].values()) else 0.0
        return round((rc + pc) / 2, 2)

    def apply(self, patch: Dict, auto_commit: bool = True) -> Dict:
        """Apply only if policy allows"""
        conf = self.confidence(patch)
        if self.policy.allow(patch, conf):
            result = execute_patch(patch, auto_commit)
            patch["status"] = "applied"
            patch["rollback"]["available"] = True
            self.history.append(patch)
            return result
        patch["status"] = "blocked"
        return {"status": "blocked", "reason": "policy_check_failed"}

    def rollback(self, patch_id: str) -> Dict:
        """Revert safely"""
        return safe_rollback(patch_id)

    def status(self, patch_id: str) -> Optional[Dict]:
        """Get patch state"""
        return next((p for p in self.history if p["id"] == patch_id), None)

    def artifactize(self, patch: Dict) -> Dict:
        """Convert verified patch → Knowledge Artifact"""
        return {
            "type": "code-pattern",
            "problem": patch["reason"],
            "patch": patch["files"],
            "verification": patch["validation"],
            "confidence": self.confidence(patch),
            "repository": patch.get("target"),
            "source": "patch-skill"
        }


class PatchPolicy:
    """Guardrails — never bypass branch protection"""
    def __init__(self):
        self.rules = {
            "require_clean_worktree": True,
            "require_diff_review": True,
            "require_tests": True,
            "require_security_scan": True,
            "confidence_min": 0.90,
            "forbidden": [
                "force_push", "bypass_branch_protection",
                "disable_ci", "modify_secrets", "delete_unrelated_files"
            ]
        }

    def allow(self, patch: Dict, confidence: float) -> bool:
        val = patch.get("validation", {})
        return (confidence >= self.rules["confidence_min"] and
                val.get("syntax") == "pass" and
                val.get("conflict") == "pass" and
                val.get("tests") == "pass" and
                val.get("security") == "pass")


# Global instance
patch = PatchSkill()
```

---

## 📄 SKILL.md — Documentation
```markdown
# 🛠️ Patch Skill — Controlled Change Management
**Purpose:** Minimal, auditable, reversible code changes  
**Principle:** Smallest safe change — never rewrite entire project

## 🧩 Core API
- `patch.create()` → Build patch object
- `patch.generate()` → Unified diff
- `patch.analyze()` → Risk/scope
- `patch.validate()` → Syntax/conflict/tests/security
- `patch.preview()` → Dry run
- `patch.confidence()` → Score 0–1
- `patch.apply()` → Auto/Manual
- `patch.rollback()` → Revert
- `patch.artifactize()` → → Knowledge

## 📋 Lifecycle
Request → Analyze → Generate → Preview → Validate → Policy Check → Apply → Test → Knowledge

## 🛡️ Policy Guardrails
- ✅ No force push
- ✅ No bypass branch protection
- ✅ No secret modification
- ✅ Tests/Security required
- ✅ Confidence ≥ 0.90

## 🔗 Integrations
- debug-error → root cause → patch
- claude → suggest → validate → apply
- github-coding → PR/CI/Review
- create-knowledge-artifact → save verified patterns
```

---

## 📄 Example Patch Object
```json
{
  "id": "patch_001",
  "type": "bugfix",
  "status": "proposed",
  "target": "main",
  "issue": "#123",
  "files": [{"path": "app/api.py", "lines": "42-51"}],
  "reason": "500 error on dependency init",
  "risk": {"level": "low", "root_cause_confidence": 0.96},
  "validation": {
    "syntax": "pass", "conflict": "pass",
    "tests": "pass", "security": "pass"
  },
  "confidence": 0.94,
  "rollback": {"available": true}
}
```

---

## 🔗 Ecosystem Integration
```
AI Orchestrator
    ├── debug-error → root cause → patch.generate()
    ├── claude → propose → patch.validate()
    └── github-coding → PR → CI → patch.apply()
patch
    ├── analyze → risk
    ├── validate → syntax/tests/security
    ├── apply → policy check
    └── artifactize → Knowledge Artifact
```

---

## 🚀 Usage Example
```python
from skills.patch import patch

# 1. Create
p = patch.create(
    files=[{"path": "app/api.py", "content": "fixed code"}],
    reason="Fix 500 on init",
    issue="#123",
    target_branch="main"
)

# 2. Analyze & Validate
p = patch.analyze(p)
p = patch.validate(p)

# 3. Preview
print(patch.preview(p))

# 4. Apply if confident
if patch.confidence(p) >= 0.9:
    result = patch.apply(p)
    # → Auto-saved as Knowledge Artifact
```

---

## 🧪 Policy Logic
```
Confidence ≥ 0.90
+ Syntax OK
+ No Conflicts
+ Tests Pass
+ Security OK
+ Worktree Clean
→ ✅ AUTO APPLY

ELSE
→ ⏳ REVIEW REQUIRED
```

---

## 📥 Ready to Add
```bash
mkdir -p skills/patch/{analyze,generate,validate,apply,tests}
# Copy all files above
git add skills/patch/
git commit -m "feat: add Patch Skill — controlled change management layer"
```

---

## ✅ Key Advantage
**Patch ≠ Coding Agent**  
Agents decide *what* → Patch controls *how* → Safe, auditable, reversible

Would you like me to write **full implementation files** for each submodule (`diff.py`, `apply.py`, etc.)? 🧩✅
