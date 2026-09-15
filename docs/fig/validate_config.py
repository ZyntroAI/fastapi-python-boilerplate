#!/usr/bin/env python3
"""Validate docs/fig/config/*.json — parse, schema shape, and source fidelity."""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CFG = HERE / "config"
fails = []


def check(label, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + label + (f"  -> {detail}" if detail else ""))
    if not ok:
        fails.append(label)


def load(name):
    with open(CFG / name, encoding="utf-8") as fh:
        return json.load(fh)


# 1. every config file parses
expected = [
    "fig.organization.json",
    "fig.components.json",
    "masterfiles.json",
    "fig.security.json",
    "roles.json",
    "github-rules.json",
    "fig.audit-event.schema.json",
    "examples/audit-event.example.json",
]
for name in expected:
    try:
        load(name)
        check(f"parses: {name}", True)
    except Exception as exc:  # noqa: BLE001
        check(f"parses: {name}", False, str(exc))

# 2. values match the source document
org = load("fig.organization.json")
check("org.name == ZyntroAI", org["name"] == "ZyntroAI", org["name"])
check("org.mode == organization", org["mode"] == "organization")
check("ownership all true", all(org["ownership"].values()), str(org["ownership"]))

mf = load("masterfiles.json")
check("masterfiles.mode == strict", mf["mode"] == "strict")
check("masterfiles immutable+ownerOnly", mf["immutable"] and mf["ownerOnly"])
src_paths = {
    "/api/v1/masterfiles",
    "/api/v1/system",
    "/api/v1/config",
    "/api/v1/settings",
}
check(
    "protectedPaths == source (4)",
    set(mf["protectedPaths"]) == src_paths,
    str(mf["protectedPaths"]),
)
check(
    "protectedPaths start with /api/v1/",
    all(p.startswith("/api/v1/") for p in mf["protectedPaths"]),
)

sec = load("fig.security.json")
sec_flags = {k: v for k, v in sec.items() if not k.startswith("$")}
check("security: 5 flags all true", len(sec_flags) == 5 and all(sec_flags.values()),
      str(sec_flags))

roles = load("roles.json")["roles"]
check("roles: 4 defined", len(roles) == 4, str(sorted(roles)))
check("VIEWER read-only", roles["VIEWER"] == ["READ"])
check("ORG_OWNER has SYSTEM", "SYSTEM" in roles["ORGANIZATION_OWNER"])
check("MAINTAINER == READ,WRITE", set(roles["MAINTAINER"]) == {"READ", "WRITE"})
check("ADMIN == READ,WRITE,UPDATE", set(roles["ADMIN"]) == {"READ", "WRITE", "UPDATE"})

gh = load("github-rules.json")["masterfiles"]
check("github require_review_count == 2", gh["require_review_count"] == 2)
check("github: 5 rules, all true except count",
      all(v is True for k, v in gh.items() if k != "require_review_count"))

comp = load("fig.components.json")
check("components: 13", len(comp["components"]) == 13, str(len(comp["components"])))
check("organizationTree: 7", len(comp["organizationTree"]) == 7,
      str(comp["organizationTree"]))

# 3. audit example validates against its own schema (required keys + enum)
audit = load("examples/audit-event.example.json")
schema = load("fig.audit-event.schema.json")
missing = [k for k in schema["required"] if k not in audit]
check("audit example has all required keys", not missing, str(missing))
check("audit action in enum", audit["action"] in schema["properties"]["action"]["enum"],
      audit["action"])
check("audit timestamp RFC3339",
      bool(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", audit["timestamp"])),
      audit["timestamp"])
check("audit resource is a protected path", audit["resource"] in src_paths,
      audit["resource"])

# 4. no jsx pseudocode left in the config files
for name in expected:
    text = (CFG / name).read_text(encoding="utf-8")
    leaked = [ln for ln in text.splitlines() if "FIG." in ln and ":" in ln and "{" in ln]
    check(f"no jsx pseudocode in {name}", not leaked)

print()
if fails:
    print(f"{len(fails)} FAILED: {fails}")
    sys.exit(1)
print("ALL FIG CONFIG CHECKS PASSED")
