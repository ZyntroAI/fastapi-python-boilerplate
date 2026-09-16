#!/usr/bin/env bash
# Verify deliverables/docker-stack/ against the real app.
#
# Runs without a Docker daemon: it checks the things that can be checked from
# source (compose validity, dependency closure, health paths, env contract) and
# says plainly what it cannot check.
#
# Usage:  bash deliverables/docker-stack/verify-stack.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
FAIL=0
ok()   { printf '  \033[32mok\033[0m   %s\n' "$1"; }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAIL=1; }
skip() { printf '  \033[33mskip\033[0m %s\n' "$1"; }
step() { printf '\n\033[1m%s\033[0m\n' "$1"; }

cd "$ROOT" || exit 1

step "1. Files present"
for f in Dockerfile .dockerignore docker-compose.yml requirements.stack.txt \
         Makefile.docker .env.stack.example nginx/nginx.conf README.md; do
  [ -f "$HERE/$f" ] && ok "$f" || bad "missing $f"
done

step "2. docker-compose.yml is valid YAML with the expected services"
python3 - "$HERE/docker-compose.yml" <<'PY'
import sys, yaml
d = yaml.safe_load(open(sys.argv[1]))
svcs = set(d.get("services", {}))
want = {"api", "postgres", "redis", "proxy"}
missing = want - svcs
if missing:
    print(f"  \033[31mFAIL\033[0m missing services: {sorted(missing)}"); sys.exit(1)
api = d["services"]["api"]
ctx = api["build"]["context"]
if ctx != "../..":
    print(f"  \033[31mFAIL\033[0m api build context is {ctx!r}, expected '../..'"); sys.exit(1)
if "postgres" not in api.get("depends_on", {}) or "redis" not in api.get("depends_on", {}):
    print("  \033[31mFAIL\033[0m api does not depend on postgres + redis"); sys.exit(1)
print(f"  \033[32mok\033[0m   services: {sorted(svcs)}")
PY
[ $? -eq 0 ] || FAIL=1

step "3. Dockerfile actually builds this app (not Node)"
if grep -q "FROM node" "$HERE/Dockerfile"; then
  bad "Dockerfile uses a Node base image"
else
  ok "Python base image"
fi
grep -q "app.main:app" "$HERE/Dockerfile" && ok "CMD targets app.main:app" || bad "CMD does not target app.main:app"
grep -q "deliverables/docker-stack/requirements.stack.txt" "$HERE/Dockerfile" \
  && ok "installs requirements.stack.txt" || bad "does not install requirements.stack.txt"

step "4. HEALTHCHECK uses the exact path /health (not /health/)"
# /health/ returns 307 and curl -f treats 3xx as success, so probing it would
# report healthy without proving anything. The HEALTHCHECK spans two lines via
# a backslash continuation, so collapse continuations before matching.
python3 - "$HERE/Dockerfile" "$HERE/docker-compose.yml" <<'PY'
import re, sys, yaml
dockerfile = sys.argv[1]
raw = open(dockerfile).read()
joined = re.sub(r"\\\s*\n\s*", " ", raw)          # collapse line continuations
m = re.search(r"HEALTHCHECK[^\n]*?CMD\s+(\S+.*?)(?:\s*\|\||\n)", joined)
cmd = m.group(1).strip() if m else ""
ok = cmd.endswith("/health\"") or cmd.endswith("/health")
print(f"  {'\033[32mok\033[0m  ' if ok else '\033[31mFAIL\033[0m'} Dockerfile probes ...{cmd[-30:]}")
bad = 0 if ok else 1

comp = yaml.safe_load(open(sys.argv[2]))
test = comp["services"]["api"]["healthcheck"]["test"]
joined_with = " ".join(map(str, test))
ok2 = joined_with.rstrip('"').endswith("/health")
print(f"  {'\033[32mok\033[0m  ' if ok2 else '\033[31mFAIL\033[0m'} compose probes ...{joined_with[-30:]}")
sys.exit(bad + (0 if ok2 else 1))
PY
[ $? -eq 0 ] || FAIL=1

step "5. Dependency closure: requirements.txt + requirements.stack.txt import app.main"
VENV=/tmp/verify_stack_venv
rm -rf "$VENV"
python3 -m venv "$VENV" 2>/dev/null
"$VENV/bin/pip" install -q --upgrade pip 2>/dev/null
if "$VENV/bin/pip" install -q -r requirements.txt -r "$HERE/requirements.stack.txt" 2>/dev/null; then
  if "$VENV/bin/python" -c "import sys; sys.path.insert(0,'.'); import app.main" 2>/dev/null; then
    ok "import app.main succeeds with requirements.txt + requirements.stack.txt"
  else
    bad "import app.main still fails with both requirements files"
  fi
else
  bad "pip install failed"
fi

step "6. requirements.txt alone is NOT sufficient (the reason requirements.stack.txt exists)"
VENV2=/tmp/verify_stack_venv_bare
rm -rf "$VENV2"
python3 -m venv "$VENV2" 2>/dev/null
"$VENV2/bin/pip" install -q --upgrade pip 2>/dev/null
"$VENV2/bin/pip" install -q -r requirements.txt 2>/dev/null
if "$VENV2/bin/python" -c "import sys; sys.path.insert(0,'.'); import app.main" 2>/dev/null; then
  printf '  \033[33mnote\033[0m requirements.txt alone now works — requirements.stack.txt may be redundant\n'
else
  ok "requrements.txt alone fails, as expected (stack file is needed)"
fi

step "7. Health paths return the documented status codes"
"$VENV/bin/python" <<'PY'
import sys
sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app, follow_redirects=False)
want = {"/health": 200, "/health/ready": 200, "/health/live": 200, "/health/": 307}
bad = 0
for url, code in want.items():
    got = c.get(url).status_code
    mark = "\033[32mok\033[0m  " if got == code else "\033[31mFAIL\033[0m"
    print(f"  {mark} {url:16} -> {got} (expected {code})")
    if got != code:
        bad += 1
sys.exit(1 if bad else 0)
PY
[ $? -eq 0 ] || FAIL=1

step "8. Every env var the compose file sets is one the app reads"
python3 - "$HERE/docker-compose.yml" <<'PY'
import re, sys, pathlib, yaml
compose = yaml.safe_load(open(sys.argv[1]))
envs = set(compose["services"]["api"]["environment"])
src = ""
for f in ("app/config.py", "app/core/config.py"):
    src += pathlib.Path(f).read_text(encoding="utf-8", errors="ignore")
# plain settings fields  (NAME: type = ...)
fields = set(re.findall(r"^\s*([A-Z_][A-Z0-9_]*)\s*:", src, re.M))
# pydantic properties     (def NAME(self) -> ...)  e.g. FRONTEND_URL, CORS_ORIGINS
fields |= set(re.findall(r"^\s*def\s+([A-Z_][A-Z0-9_]*)\s*\(\s*self", src, re.M))
infra = {"PORT"}          # container-level, not an app setting
unknown = {e for e in envs if e not in fields and e not in infra}
if unknown:
    print(f"  \033[31mFAIL\033[0m compose sets vars the app never reads: {sorted(unknown)}")
    sys.exit(1)
print(f"  \033[32mok\033[0m   all {len(envs)} env vars are read by the app")
for k in ("JWT_SECRET", "JWT_SECRET_KEY", "FRONTEND_URL"):
    print(f"       {k:16} declared by app: {k in fields}")
PY
[ $? -eq 0 ] || FAIL=1

step "9. .dockerignore does not exclude what the Dockerfile copies"
python3 - "$HERE/.dockerignore" <<'PY'
import fnmatch, sys
pats = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]

def ignored(path: str) -> bool:
    """gitignore-style: last matching pattern wins, '!' negates."""
    result = False
    for raw in pats:
        neg = raw.startswith("!")
        pat = (raw[1:] if neg else raw).rstrip("/")
        if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(path, pat + "/*"):
            result = not neg
    return result

need = ["requirements.txt", "deliverables/docker-stack/requirements.stack.txt",
        "app/main.py", "main.py", "pytest.ini"]
bad = [n for n in need if ignored(n)]
for n in need:
    print(f"  {'\033[31mFAIL\033[0m' if ignored(n) else '\033[32mok\033[0m  '} {n}")
if bad:
    print(f"  \033[31mFAIL\033[0m .dockerignore excludes build inputs: {bad}")
    sys.exit(1)
PY
[ $? -eq 0 ] || FAIL=1

step "10. Makefile.docker parses and defines the documented targets"
for t in docker-build docker-up docker-down docker-logs docker-test docker-smoke docker-check docker-clean; do
  grep -q "^$t:" "$HERE/Makefile.docker" && ok "$t" || bad "target $t missing"
done

step "What this script does NOT check"
skip "the image has never been built (no docker daemon here)"
skip "the stack has never been run end to end"
skip "nginx.conf has never been loaded by nginx"
skip "Run 'make -f deliverables/docker-stack/Makefile.docker docker-up' to cover these."

rm -rf "$VENV" "$VENV2"

step "RESULT"
if [ $FAIL -eq 0 ]; then
  printf '  \033[32mAll source-level checks passed.\033[0m\n'
else
  printf '  \033[31mSome checks failed - see above.\033[0m\n'
fi
exit $FAIL
