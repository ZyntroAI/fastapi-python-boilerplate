---
id: TASK-20260916-001
title: Cross-repo patch suite — byte-faithful patches, EOL fidelity, workflow gate
status: in-progress
priority: medium
created: 2026-09-16
updated: 2026-09-16
owner: fig-ai-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: []
blocked_by:
tokens: 0
---

# TASK-20260916-001 — Cross-repo patch suite

## Goal

Three failure modes cost real time when patches move between repositories, and
none of them is about the change being made:

1. A Python text-mode round-trip normalises CRLF to LF, so a two-line append
   lands as a whole-file rewrite in the diff.
2. A CRLF file with no trailing newline passes `git apply --check` and fails
   `git am` with "patch does not apply" — the two commands disagree, and the one
   that says OK is the one you run first.
3. A workflow file with an unquoted colon will not parse, and an `uses:`
   reference on a tag parses fine while still being mutable.

Deliver a runnable suite that prevents all three, with the failure modes
reproduced against real git so the checks are demonstrably grounded.

## Steps

- [x] Audit the deliverables conventions on `main` (layout, manifest, SKILL.yaml,
      fixtures, tracker, CHANGELOG/PROBLEMS formats)
- [x] Confirm the target path is free — no existing work overwritten
- [x] Build the core package (byte-exact append, EOL fidelity, git diagnosis)
- [x] Build the workflow gate (YAML validation with line/column, SHA-pin audit)
- [x] Build the overwrite guard and the loader
- [x] Write `kernel/policy.yaml` and `manifest.json`
- [x] Generate clean and broken fixtures byte-exactly
- [x] Reproduce the CRLF `git am` failure empirically and record the result
- [x] Write and run the test suite (125 tests)
- [x] Write the two helpers, README, SKILL.yaml, and sub-skill docs
- [x] Record the task, CHANGELOG, and deliverables index entries
- [ ] Commit, push, open PR

## Verification

```sh
cd deliverables/cross-repo-patch-suite
python -m pytest -q          # 125 passed
python scripts/make_fixtures.py
```

The headline test is `test_crlf_unterminated_patch_passes_apply_check_but_fails_am`
in `tests/test_end_to_end.py`: it builds a CRLF workflow with no trailing
newline, commits a change, formats a patch, and asserts that `git apply --check`
accepts it while `git am` rejects it — then that the byte-identical LF control
passes both. Confirmed against git 2.47.3.

## Notes

- The repo's `.gitattributes` sets `* text=auto eol=lf`, which is why CRLF
  files with a missing final newline are the dangerous shape here.
- Fixtures are per failure mode rather than per file type, so each check has a
  positive case in `clean-project/` and a negative case in `broken-project/`.
- Every mutating command in the suite is a dry run unless `--apply` is passed.
