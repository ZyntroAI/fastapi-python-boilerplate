#!/usr/bin/env python3
"""Verify every pinned SHA actually exists in its upstream repo (guards against fake SHAs)."""
import glob, json, os, re, subprocess, sys

REPO = "/tmp/fpb_pin"
WF = os.path.join(REPO, ".github", "workflows")
USES = re.compile(r"uses:\s*([A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)?)@([0-9a-f]{40})")

def base(a):
    return "/".join(a.split("/")[:2])

def check(repo, sha):
    out = subprocess.run(
        ["curl", "-s", "--max-time", "25", "-o", "/dev/null", "-w", "%{http_code}",
         f"https://github.com/{repo}/commit/{sha}"],
        capture_output=True, text=True)
    return out.stdout.strip()

pairs = {}
for f in sorted(glob.glob(os.path.join(WF, "*.yml")) + glob.glob(os.path.join(WF, "*.yaml"))):
    for m in USES.finditer(open(f, encoding="utf-8").read()):
        pairs.setdefault((base(m.group(1)), m.group(2)), set()).add(os.path.basename(f))

print(f"distinct (action, sha) pairs: {len(pairs)}\n")
bad = []
for (repo, sha), files in sorted(pairs.items()):
    code = check(repo, sha)
    ok = code == "200"
    if not ok:
        bad.append((repo, sha, code, sorted(files)))
    print(f"{'OK  ' if ok else 'BAD '} {repo}@{sha[:12]}  [{code}]  <- {', '.join(sorted(files))}")

print(f"\ninvalid: {len(bad)}")
if bad:
    for r, s, c, fs in bad:
        print(f"  {r}@{s} http={c} in {fs}")
sys.exit(1 if bad else 0)
