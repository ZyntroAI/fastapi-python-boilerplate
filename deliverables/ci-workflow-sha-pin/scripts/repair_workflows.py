#!/usr/bin/env python3
"""Repair the 4 pre-existing broken workflow YAML files, then re-validate."""
import os, re, sys, glob

import yaml

REPO = "/tmp/fpb_pin"
WF = os.path.join(REPO, ".github", "workflows")
log = []

# ---------------------------------------------------------------- 1. secret-scan.yml
p = os.path.join(WF, "secret-scan.yml")
s = open(p, encoding="utf-8").read()
before = s
s = s.replace("  workflow_dispatch;\n", "  workflow_dispatch:\n")
if s != before:
    open(p, "w", encoding="utf-8").write(s)
    log.append("secret-scan.yml: 'workflow_dispatch;' -> 'workflow_dispatch:'")

# ------------------------------------------------------- 2. dependabot-automerge.yml
p = os.path.join(WF, "dependabot-automerge.yml")
lines = open(p, encoding="utf-8").read().splitlines(keepends=True)
# real workflow ends at the last line before the appended markdown ("# Navigating code on GitHub")
cut = None
for i, ln in enumerate(lines):
    if ln.startswith("# Navigating code on GitHub"):
        cut = i
        break
if cut is not None:
    new = lines[:cut]
    while new and not new[-1].strip():
        new.pop()
    open(p, "w", encoding="utf-8").write("".join(new) + "\n")
    log.append(f"dependabot-automerge.yml: truncated {len(lines)-len(new)} lines of appended markdown")

# ------------------------------------------------------------------ 3. test-suite.yml
p = os.path.join(WF, "test-suite.yml")
lines = open(p, encoding="utf-8").read().splitlines(keepends=True)
start = end = None
for i, ln in enumerate(lines):
    if ln.strip().startswith("```yaml") and start is None:
        start = i + 1
    elif ln.strip() == "```" and start is not None:
        end = i
        break
if start is not None and end is not None:
    body = lines[start:end]
    open(p, "w", encoding="utf-8").write("".join(body).rstrip() + "\n")
    log.append(f"test-suite.yml: extracted YAML body from markdown fence (lines {start+1}-{end})")

# ------------------------------------------------------------- 4. Auto-Index-Sync.yml
p = os.path.join(WF, "Auto-Index-Sync.yml")
s = open(p, encoding="utf-8").read()
old = """            echo '#!/usr/bin/env python3
import sys
print("# Policy Snapshot\\n")
print("Source:", sys.argv[1])
' > scripts/parse_docs.py"""
new = """            cat > scripts/parse_docs.py <<'PY'
            #!/usr/bin/env python3
            import sys
            print("# Policy Snapshot\\n")
            print("Source:", sys.argv[1])
            PY"""
new = new.replace("            #!/usr/bin/env python3",
                  "#!/usr/bin/env python3", 1)
if old in s:
    s = s.replace(old, new)
    open(p, "w", encoding="utf-8").write(s)
    log.append("Auto-Index-Sync.yml: converted single-quoted echo to an indented heredoc")

print("=== repairs ===")
for l in log:
    print("  -", l)
if not log:
    print("  (nothing matched)")

print("\n=== validate ===")
bad = 0
for f in sorted(glob.glob(os.path.join(WF, "*.yml")) + glob.glob(os.path.join(WF, "*.yaml"))):
    try:
        yaml.safe_load(open(f, encoding="utf-8"))
        print("  OK  ", os.path.basename(f))
    except Exception as e:
        bad += 1
        print("  FAIL", os.path.basename(f), str(e).splitlines()[0][:90])
print(f"\nbad files: {bad}")
sys.exit(1 if bad else 0)
