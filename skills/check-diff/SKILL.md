# 🛡️ Check-Diff Skill — Diff Firewall & Preflight Analysis
**Path:** `skills/check-diff/` — Read‑only safety layer between AI agents & repository

---

## 📁 Final Structure
```
skills/check-diff/
├── SKILL.md               # Docs, API, pipeline
├── __init__.py            # Core export
├── collect/               # Read git state
│   ├── __init__.py
│   ├── git_diff.py        # Raw diff from HEAD/staged
│   ├── staged.py          # Staged changes only
│   └── changed_files.py   # List paths + status
├── analyze/               # Deep inspection
│   ├── __init__.py
│   ├── scope.py           # Scope creep / unexpected files
│   ├── impact.py          # Risk & blast radius
│   ├── security.py        # Dangerous patterns
│   ├── secrets.py         # Detect keys/passwords
│   ├── dependencies.py    # package.json/pyproject.toml changes
│   └── tests.py           # Test coverage & modified tests
├── policy/                # Rules & thresholds
│   ├── rules.yaml         # Secrets/dangerous/paths
│   └── thresholds.yaml    # Risk scoring levels
├── report/                # Output formats
│   ├── summary.py         # Human‑friendly text
│   └── json.py            # Machine‑readable JSON
└── tests/                 # Skill self‑tests
```

---

## 🧠 Core API (`__init__.py`)
```python
"""
🛡️ Check-Diff Skill — Diff Firewall
Purpose: Read‑only preflight analysis before patch/commit/PR
Permissions: READ‑ONLY — no write, no modify
"""
from typing import Dict, List, Optional
from .collect.git_diff import get_raw_diff, get_changed_files
from .analyze.scope import check_scope
from .analyze.security import check_security
from .analyze.secrets import scan_secrets
from .analyze.dependencies import check_deps
from .analyze.tests import check_test_impact
from .analyze.impact import calculate_risk
from .policy.rules import load_rules
from .policy.thresholds import load_thresholds
from .report.summary import human_summary
from .report.json import json_report

class CheckDiffSkill:
    """
    Diff Firewall: AI → Patch → Check‑Diff → Repository
    READ‑ONLY: never modifies code
    """
    def __init__(self):
        self.rules = load_rules()
        self.thresholds = load_thresholds()
        self.permissions = {"read": ["git_diff", "repo", "tests"], "write": [], "execute": ["analysis"]}

    def collect(self, mode: str = "staged") -> Dict:
        """Get raw diff + file list"""
        return {
            "diff": get_raw_diff(mode),
            "files": get_changed_files(mode)
        }

    def analyze(self, diff_data: Dict, expected_scope: Optional[List[str]] = None) -> Dict:
        """Run full analysis pipeline"""
        scope_ok, scope_findings = check_scope(diff_data["files"], expected_scope)
        sec_ok, sec_findings = check_security(diff_data["diff"], self.rules)
        secr_ok, secr_findings = scan_secrets(diff_data["diff"], self.rules)
        dep_ok, dep_findings = check_deps(diff_data["files"], diff_data["diff"])
        test_ok, test_findings = check_test_impact(diff_data["files"], diff_data["diff"])

        findings = scope_findings + sec_findings + secr_findings + dep_findings + test_findings
        risk = calculate_risk(findings, diff_data["files"], self.thresholds)

        return {
            "status": self._status(risk),
            "risk": risk,
            "scope": scope_ok,
            "security": sec_ok,
            "secrets": secr_ok,
            "dependencies": dep_ok,
            "tests": test_ok,
            "files_changed": len(diff_data["files"]),
            "findings": findings
        }

    def run(self, expected_scope: Optional[List[str]] = None) -> Dict:
        """Full pipeline: collect → analyze → report"""
        data = self.collect()
        result = self.analyze(data, expected_scope)
        result["human"] = human_summary(result)
        result["json"] = json_report(result)
        return result

    def _status(self, risk: float) -> str:
        if risk >= self.thresholds["critical"]: return "FAIL"
        if risk >= self.thresholds["high"]: return "REVIEW"
        if risk >= self.thresholds["medium"]: return "WARN"
        return "PASS"

    # Shortcuts
    def check_scope(self, files: List[str], expected: List[str]): return check_scope(files, expected)
    def check_security(self, diff: str): return check_security(diff, self.rules)
    def check_secrets(self, diff: str): return scan_secrets(diff, self.rules)
    def check_dependencies(self): return check_deps()
    def check_tests(self): return check_test_impact()
    def risk(self): return self.run()["risk"]
    def status(self): return self.run()["status"]
    def report(self): return self.run()["human"]


# Global instance
check_diff = CheckDiffSkill()
```

---

## 📄 SKILL.md — Documentation
```markdown
# 🛡️ Check-Diff Skill — Diff Firewall
**Purpose:** Read‑only preflight safety before patch, commit, PR  
**Permissions:** READ‑ONLY — NO write/execute on repository  
**Role:** Firewall between AI agents & actual code

## ⚙️ Pipeline
Git Diff → Changed Files → Parse Hunks → Classify → Scope → Security → Secrets → Dependencies → Tests → Risk → PASS/WARN/FAIL

## 🧩 Core API
- `check_diff.collect()` → Raw diff + files
- `check_diff.analyze()` → Full checks
- `check_diff.run(expected_scope=None)` → Full pipeline + report
- `check_diff.check_scope()` → Scope creep
- `check_diff.check_security()` → Dangerous patterns
- `check_diff.check_secrets()` → Keys/passwords
- `check_diff.check_dependencies()` → Package changes
- `check_diff.check_tests()` → Test coverage
- `check_diff.risk()` → 0.0–1.0 score
- `check_diff.status()` → PASS/WARN/REVIEW/FAIL
- `check_diff.report()` → Human + JSON

## 📋 Result Schema
```json
{
  "status": "PASS",
  "risk": "low",
  "risk_score": 0.12,
  "files_changed": 4,
  "additions": 87,
  "deletions": 21,
  "checks": {
    "scope": true,
    "security": true,
    "secrets": true,
    "dependencies": true,
    "tests": true
  },
  "findings": [],
  "human": "DIFF CHECK PASS...",
  "json": "..."
}
```

## 🧠 Scope Creep Detection
**Requirement:** Fix auth timeout → Expected: `backend/auth.py`  
**Diff:** `auth.py + navbar.jsx + schema.sql + docker-compose.yml`  
**Output:** `WARN: Unexpected files! Expected: [auth.py] Detected: [navbar, schema, compose]`

## 🔒 Security Rules (`rules.yaml`)
```yaml
secrets: [api_key, access_token, private_key, password, client_secret]
dangerous: [chmod_777, shell_injection, eval, exec, disable_security]
protected: [.github/workflows/, infrastructure/, terraform/, kubernetes/]
```

## 📊 Risk & Policy (`thresholds.yaml`)
```yaml
thresholds:
  low: 0.00
  medium: 0.35
  high: 0.65
  critical: 0.85
actions:
  low: auto_continue
  medium: review_required
  high: approval_required
  critical: block
```

## 🔗 Ecosystem Flow
```
AI Agent → Decide What
    ↓
Patch Skill → Generate Minimal Diff
    ↓
✅ Check‑Diff (THIS SKILL)
    ↓
PASS → Apply
WARN → Preview/Review
FAIL → Block/Reject
    ↓
Tests → Security → GitHub → Knowledge
```

## ✅ Permissions
```yaml
permissions:
  read: [git_diff, repository, tests, workflows]
  write: []
  execute: [git_diff, static_analysis]
```

## 🚀 Usage
```python
from skills.check_diff import check_diff

# Define expected scope
scope = ["backend/auth.py"]

# Run full check
result = check_diff.run(expected_scope=scope)

# Output
print(result["human"])
print(result["json"])

# Decide
if result["status"] == "PASS":
    patch.apply()
elif result["status"] in ["WARN", "REVIEW"]:
    request_review()
else:
    block_and_alert()
```
```

---

## 📄 Policy Files

### `policy/rules.yaml`
```yaml
secrets:
  - api_key
  - access_token
  - private_key
  - password
  - client_secret
  - secret_key
  - jwt_secret
  - db_password

dangerous:
  - chmod 777
  - eval(
  - exec(
  - shell=True
  - subprocess.run(shell=
  - disable_security_check
  - allow_origin="*"
  - hardcoded_credential

protected_paths:
  - .github/workflows/
  - infrastructure/
  - terraform/
  - kubernetes/
  - .env
  - secrets/

scope_enforcement:
  strict: true
  allow_extra: false
```

### `policy/thresholds.yaml`
```yaml
risk_weights:
  scope_change: 0.30
  security_issue: 0.45
  secret_detected: 0.60
  dependency_change: 0.15
  protected_file_change: 0.50
  test_coverage_drop: 0.25

thresholds:
  low: 0.00
  medium: 0.35
  high: 0.65
  critical: 0.85

actions:
  low: auto_continue
  medium: review_required
  high: approval_required
  critical: block
```

---

## 📄 Example Output
**Human:**
```
DIFF CHECK ────────────────────────
✅ Status: PASS
📊 Risk: LOW (0.12)
📁 Files: 4 (+87 / -21)
🔍 Scope: ✅ MATCH
🔒 Security: ✅ OK
🔑 Secrets: ✅ NONE
📦 Dependencies: ✅ UNCHANGED
🧪 Tests: ✅ COVERAGE OK
⚠️ Findings: 0
→ Decision: SAFE TO CONTINUE
───────────────────────────────────
```

**JSON:**
```json
{
  "status": "pass",
  "risk": "low",
  "risk_score": 0.12,
  "files_changed": 4,
  "additions": 87,
  "deletions": 21,
  "checks": {
    "scope": true,
    "security": true,
    "secrets": true,
    "dependencies": true,
    "tests": true
  },
  "findings": []
}
```

---

## 🔗 Integration with Patch Skill
```python
from skills.patch import patch
from skills.check_diff import check_diff

# 1. Generate patch
p = patch.create(...)
p = patch.generate(p)
p = patch.preview(p)

# 2. Firewall check
scope = p["files"]
check = check_diff.run(expected_scope=scope)

# 3. Policy gate
if check["status"] == "PASS":
    patch.apply(p)
elif check["status"] == "WARN":
    human_review()
else:
    patch.reject()
```

---

## 🚀 Install & Merge
```bash
mkdir -p skills/check-diff/{collect,analyze,policy,report,tests}
# Copy all files above
git add skills/check-diff/
git commit -m "feat: add Check-Diff Skill — read-only diff firewall & preflight analysis"
git push -u origin zyntromedia-patch-7
```

---

## ✅ Key Principles
- **READ‑ONLY:** No write, no modify, no bypass
- **Scope‑First:** Block AI “scope creep”
- **Security‑Built‑In:** Secrets + dangerous patterns
- **Clear Signals:** PASS/WARN/REVIEW/FAIL
- **Fits Flow:** Patch → Check → Apply → GitHub

---

Ready to merge into your ecosystem! 🛡️✅
