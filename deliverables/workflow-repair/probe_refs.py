"""Probe every `uses:` target in the repo's workflows and report validity."""
import json, os, re, subprocess, sys, urllib.request, urllib.error

REPO = "/workspace/H7tGkmt5NUfW1dxEb7zSB64VDoY2/7aa25c80-ed0f-4616-a14d-0531cab130f7/raw_data/fpsb"
WF = os.path.join(REPO, ".github/workflows")

def api(path):
    req = urllib.request.Request("https://api.github.com" + path, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "fig-probe"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, None

targets = {}   # "owner/repo@ref" -> set(files)
for fn in sorted(os.listdir(WF)):
    p = os.path.join(WF, fn)
    if not os.path.isfile(p):
        continue
    for ln, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
        m = re.search(r"uses:\s*([^\s#]+)", line)
        if not m:
            continue
        spec = m.group(1)
        if spec.startswith("./") or "${{" in spec:
            continue
        targets.setdefault(spec, set()).add(f"{fn}:{ln}")

report = []
for spec, locs in sorted(targets.items()):
    if "@" not in spec:
        kind, code, detail = "NO_REF", None, "no @ref"
    else:
        name, ref = spec.rsplit("@", 1)
        parts = name.split("/")
        repo = "/".join(parts[:2])
        subpath = "/".join(parts[2:])
        if re.fullmatch(r"[0-9a-f]{40}", ref):
            code, _ = api(f"/repos/{repo}/git/commits/{ref}")
            kind = "SHA"
            detail = "valid SHA" if code == 200 else f"HTTP {code} — SHA does not exist"
        else:
            code, d = api(f"/repos/{repo}/git/ref/tags/{ref}")
            kind = "TAG"
            detail = f"HTTP {code}"
            if code == 200:
                detail = f"tag -> {d['object']['type']} {d['object']['sha'][:12]}"
    report.append({"spec": spec, "kind": kind, "http": code, "detail": detail,
                   "locations": sorted(locs)})

json.dump(report, open("ref_probe.json", "w"), indent=2)
for r in report:
    flag = "OK  " if r["http"] == 200 else "BAD "
    print(f"{flag} {r['spec']:<62} {r['detail']}")
bad = [r for r in report if r["http"] != 200]
print(f"\ntotal refs: {len(report)}   valid: {len(report)-len(bad)}   invalid: {len(bad)}")
