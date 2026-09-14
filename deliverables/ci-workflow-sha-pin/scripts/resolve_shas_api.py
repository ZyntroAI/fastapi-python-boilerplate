#!/usr/bin/env python3
"""Resolve real commit SHAs for action refs via the GitHub API (works where git ls-remote is rewritten)."""
import json, subprocess

REFS = [
    ("actions/checkout", "v4"),
    ("actions/upload-artifact", "v4"),
    ("actions/setup-python", "v5"),
    ("actions/setup-java", "v4"),
    ("actions/github-script", "v7"),
    ("actions/download-artifact", "v4"),
    ("actions/upload-pages-artifact", "v3"),
    ("actions/deploy-pages", "v5"),
    ("actions/configure-pages", "v5"),
    ("subosito/flutter-action", "v2"),
    ("somaz94/compress-decompress", "v1"),
    ("wzieba/Firebase-Distribution-Github-Action", "v1"),
    ("r0adkll/sign-android-release", "v1"),
    ("pascalgn/automerge-action", "v0.16.4"),
    ("gitleaks/gitleaks-action", "v2"),
    ("github/codeql-action", "v3"),
    ("dependabot/fetch-metadata", "v2"),
    ("codecov/codecov-action", "v4"),
    ("apple-actions/upload-testflight-build", "v1"),
    ("apple-actions/import-codesign-certs", "v3"),
    ("apple-actions/download-provisioning-profiles", "v1"),
    ("softprops/action-gh-release", "v2"),
    ("docker/login-action", "v3"),
    ("docker/build-push-action", "v6"),
    ("ZyntroAI/ai-codefix-action", "v1"),
]

def api(path):
    out = subprocess.run(["curl", "-s", "--max-time", "25", f"https://api.github.com{path}"],
                         capture_output=True, text=True)
    try:
        return json.loads(out.stdout)
    except Exception:
        return {}

def resolve(repo, tag):
    d = api(f"/repos/{repo}/git/ref/tags/{tag}")
    if "object" in d:
        obj = d["object"]
        if obj.get("type") == "tag":  # annotated -> dereference to commit
            t = api(f"/repos/{repo}/git/tags/{obj['sha']}")
            if "object" in t:
                return t["object"]["sha"], "ok(deref)"
        return obj.get("sha"), "ok"
    # some tags may live under refs/tags with different naming; try commits endpoint
    return None, "not-found"

result = {}
for repo, tag in REFS:
    sha, status = resolve(repo, tag)
    result[f"{repo}@{tag}"] = {"sha": sha, "status": status}
    flag = "OK " if sha and len(sha) == 40 else "!! "
    print(f"{flag}{repo}@{tag} -> {sha} ({status})")

with open("/tmp/fpb_pin/resolved_shas.json", "w") as f:
    json.dump(result, f, indent=2)
missing = [k for k, v in result.items() if not v["sha"]]
print("\nmissing:", missing if missing else "none")
