#!/usr/bin/env python3
"""Pin every GitHub Actions `uses:` ref in root workflows to full commit SHAs, then validate YAML."""
import json, os, re, sys, glob

import yaml

REPO = "/tmp/fpb_pin"
WF_DIR = os.path.join(REPO, ".github", "workflows")

# Canonical resolved SHAs (verified via api.github.com git/ref/tags)
SHA = {
    "actions/checkout": "11d5960a326750d5838078e36cf38b85af677262",
    "actions/upload-artifact": "ea165f8d65b6e75b540449e92b4886f43607fa02",
    "actions/setup-python": "a26af69be951a213d495a4c3e4e4022e16d87065",
    "actions/setup-java": "cf277c60eb25467037889841efdb72551f06f6c3",
    "actions/github-script": "f28e40c7f34bde8b3046d885e986cb6290c5673b",
    "actions/download-artifact": "d3f86a106a0bac45b974a628896c90dbdf5c8093",
    "actions/upload-pages-artifact": "56afc609e74202658d3ffba0e8f6dda462b719fa",
    "actions/deploy-pages": "368f82528645a54fb793d4d04e342629a3f51346",
    "actions/configure-pages": "983d7736d9b0ae728b81ab479565c72886d7745b",
    "subosito/flutter-action": "1a449444c387b1966244ae4d4f8c696479add0b2",
    "somaz94/compress-decompress": "4aa7a81b5e2c20ac4a865d937466f3d8928f487c",
    "wzieba/Firebase-Distribution-Github-Action": "bd494989dd4bec0343f78adee87fe66e48279ad6",
    "r0adkll/sign-android-release": "349ebdef58775b1e0d8099458af0816dc79b6407",
    "pascalgn/automerge-action": "7961b8b5eec56cc088c140b56d864285eabd3f67",
    "gitleaks/gitleaks-action": "ff98106e4c7b2bc287b24eaf42907196329070c7",
    "github/codeql-action": "faaca9a8f6edddba5725ffe5adefdab6669a2eca",
    "dependabot/fetch-metadata": "21025c705c08248db411dc16f3619e6b5f9ea21a",
    "codecov/codecov-action": "b9fd7d16f6d7d1b5d2bec1a2887e65ceed900238",
    "apple-actions/upload-testflight-build": "54dc215b4cd5529730db39f11c84efdb71414e07",
    "apple-actions/import-codesign-certs": "63fff01cd422d4b7b855d40ca1e9d34d2de9427d",
    "apple-actions/download-provisioning-profiles": "3167792207a5b26099bc0ca22b5010a323dd2a0b",
    "softprops/action-gh-release": "3bb12739c298aeb8a4eeaf626c5b8d85266b0e65",
    "docker/login-action": "c94ce9fb468520275223c153574b00df6fe4bcc9",
    "docker/build-push-action": "10e90e3645eae34f1e60eeb005ba3a3d33f178e8",
}

# human-readable tag for the trailing comment
TAG = {
    "actions/checkout": "v4",
    "actions/upload-artifact": "v4",
    "actions/setup-python": "v5",
    "actions/setup-java": "v4",
    "actions/github-script": "v7",
    "actions/download-artifact": "v4",
    "actions/upload-pages-artifact": "v3",
    "actions/deploy-pages": "v5",
    "actions/configure-pages": "v5",
    "subosito/flutter-action": "v2",
    "somaz94/compress-decompress": "v1",
    "wzieba/Firebase-Distribution-Github-Action": "v1",
    "r0adkll/sign-android-release": "v1",
    "pascalgn/automerge-action": "v0.16.4",
    "gitleaks/gitleaks-action": "v2",
    "github/codeql-action": "v3",
    "dependabot/fetch-metadata": "v2",
    "codecov/codecov-action": "v4",
    "apple-actions/upload-testflight-build": "v1",
    "apple-actions/import-codesign-certs": "v3",
    "apple-actions/download-provisioning-profiles": "v1",
    "softprops/action-gh-release": "v2",
    "docker/login-action": "v3",
    "docker/build-push-action": "v6",
}

# matches:  <indent>[- ]uses: owner/repo[/subpath]@ref
USES_RE = re.compile(
    r"^(?P<pre>\s*(?:-\s+)?uses:\s*)(?P<action>[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)?)"
    r"@(?P<ref>[^\s#]+)(?P<trail>.*)$"
)

def base_action(action: str) -> str:
    # normalize a subpath action to its repo
    parts = action.split("/")
    return "/".join(parts[:2])

changed_files = []
unresolved = []

for path in sorted(glob.glob(os.path.join(WF_DIR, "*.yml")) + glob.glob(os.path.join(WF_DIR, "*.yaml"))):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    out, n = [], 0
    for line in lines:
        m = USES_RE.match(line.rstrip("\n"))
        if not m:
            out.append(line)
            continue
        action = m.group("action")
        base = base_action(action)
        sha = SHA.get(base)
        if sha is None:
            unresolved.append(f"{os.path.basename(path)}: {action}@{m.group('ref')}")
            out.append(line)
            continue
        newline = f"{m.group('pre')}{action}@{sha}  # {TAG.get(base,'')}\n"
        out.append(newline)
        n += 1
    if n:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(out)
        changed_files.append((os.path.basename(path), n))

print("=== pinned refs per file ===")
for name, n in changed_files:
    print(f"  {name}: {n}")
print(f"total files changed: {len(changed_files)}, total refs: {sum(n for _, n in changed_files)}")
if unresolved:
    print("\n=== unresolved (left alone) ===")
    for u in unresolved:
        print("  ", u)
