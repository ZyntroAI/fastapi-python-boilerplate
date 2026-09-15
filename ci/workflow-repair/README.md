# Workflow Repair Bundle

Four workflow files in `.github/workflows/` are **invalid YAML**, so those
workflows never run — and every action ref is unpinned, which the org's
SHA-pinning policy rejects at "Set up job". This directory carries the
corrected files plus a ready-to-apply patch.

They live here (not in `.github/workflows/`) because the `fig-ai-agent`
GitHub App has no `workflows` permission, so it cannot push to that path.

## What was broken

| File | Problem | Fix |
|---|---|---|
| `test-suite.yml` | Was a Markdown document wrapping the real workflow in a ` ```yaml ` fence, plus ~50 lines of chat prose | Extracted the YAML (175 → 126 lines) |
| `dependabot-automerge.yml` | ~87 lines of GitHub documentation pasted after the workflow | Truncated to the real content (121 → 34 lines) |
| `secret-scan.yml` | Typo: `workflow_dispatch;` instead of `workflow_dispatch:` | Fixed the key |
| `Auto-Index-Sync.yml` | A multi-line `echo` heredoc at column 1 broke the `run:` block scalar | Collapsed to a single-line `printf` |

Plus: all tag-style action refs across the workflows are pinned to verified
full commit SHAs, satisfying the org SHA-pinning policy.

## Apply

From a clean clone of `main`:

```bash
# Preferred — repairs the 4 files AND pins every action ref
git apply ci/workflow-repair/workflow-repair.patch
git add .github/workflows/
git commit -m "ci: repair broken workflow YAML + pin action refs to SHAs"

# Or copy just the four repaired files
cp ci/workflow-repair/repaired/*.yml .github/workflows/
```

## Verification

- All workflow files parse as YAML.
- 0 unpinned (tag-style) action refs remain.
- The patch applies cleanly to a fresh clone of `main`.
