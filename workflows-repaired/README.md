# workflows-repaired — drop-in replacement for `.github/workflows/`

`main`'s workflows currently violate the repository's own policy. GitHub enforces it:

```
The actions actions/checkout@<commit-sha>, actions/setup-python@<commit-sha>,
actions/upload-artifact@<commit-sha>, and actions/upload-artifact@v4 are not
allowed in ZyntroAI/fastapi-python-boilerplate because all actions must be
pinned to a full-length commit SHA.
```

Every CI job fails at "Set up job" because of this — before any test runs. This
directory is the repaired set.

## What was wrong

Of the 11 files in `.github/workflows/` on `main`:

- **5 do not parse as YAML** — `Auto-Index-Sync.yml`, `dependabot-automerge.yml`, `secret-scan.yml`, `test-suite.yml`, and `github-actions-autodebug-autorerun`.
- **53 `uses:` refs are pinned to tags or branches**, not full commit SHAs (`build-compress-all-platforms.yml` alone has 23).
- **`github-actions-autodebug-autorerun` has no `.yml` extension**, so GitHub has never run it. It also references `ZyntroAI/ai-codefix-action@v1`, which is not a repository — so it would fail at its first step even once renamed.

## What this set changes

All 10 real workflow files parse and every `uses:` ref is a 40-character SHA.
`release_drafter.yaml` was already clean and is byte-identical to `main`.
`github-actions-autodebug-autorerun` is renamed to `.yml`.

## How to apply

Either swap the directory wholesale:

```bash
git rm -r .github/workflows
cp -r workflows-repaired/.github/workflows .github/workflows
git add .github/workflows && git commit -m "ci: repair workflows (valid YAML, full-SHA pins)"
git push
```

Or apply the patch, which produces the identical tree:

```bash
git am workflows-repaired/workflows-sha-pin-repair.patch
```

The patch applies cleanly to `main` @ `92895bb` and was verified by applying it to
a clean worktree and re-running the parser and pin check over the result.

## Why it is staged here and not applied directly

Pushing a commit that touches `.github/workflows/**` is rejected by the Fig App's
missing `workflows` permission — an App-installation setting, not a repository
grant. Everything under `workflows-repaired/` is outside `.github/`, so it pushes
normally; a maintainer applies it in one command.
