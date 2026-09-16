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

## The actual root cause: six fabricated SHAs

GitHub's message is about the *policy*, but the deeper problem is that six refs on
`main` **look** pinned while referencing no commit that exists:

```
Unable to resolve action `actions/checkout@f548e57c3d3c42e288026812cd22362661c4e8d4`,
unable to find version `f548e57c3d3c42e288026812cd22362661c4e8d4`
```

Each is a near-miss of the real commit — `actions/checkout` v4.4.0 is
`11d5960a...`, while `ci.yml` says `11bd71...`:

| Ref in `main` | File | Real commit |
|---|---|---|
| `actions/checkout@f548e57c...` | `ci.yml` | `11d5960a...` (v4.4.0) |
| `actions/setup-python@5fda3b9c...` | `ci.yml` | `a26af69b...` (v5.6.0) |
| `github/codeql-action/*@977e6ce4...` (x3) | `ci.yml` | `faaca9a8...` |
| `actions/checkout@11bd7190...` | `Auto-Index-Sync.yml` | `11d5960a...` |

`ci.yml` carries 7 of them, which is why every job named after it fails. Three
literal placeholders were also left in the files — `@<commit-sha>` and
`@<pin-latest-sha>` appear verbatim in `test-and-coverage.yaml` and `ci.yml`.

## What was wrong

Of the 11 files in `.github/workflows/` on `main`:

- **5 do not parse as YAML** — `Auto-Index-Sync.yml`, `dependabot-automerge.yml`, `secret-scan.yml`, `test-suite.yml`, and `github-actions-autodebug-autorerun`.
- **53 `uses:` refs are pinned to tags or branches**, not full commit SHAs (`build-compress-all-platforms.yml` alone has 23).
- **`github-actions-autodebug-autorerun` has no `.yml` extension**, so GitHub has never run it. It also references `ZyntroAI/ai-codefix-action@v1`, which is not a repository — so it would fail at its first step even once renamed.

## What this set changes

All 10 real workflow files parse and every `uses:` ref is a real, resolvable 40-character commit SHA — all 27 distinct refs were checked against the GitHub API and every one resolves (0 unresolvable). The six fabricated refs are gone: the repaired `ci.yml` contains none of them.
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
