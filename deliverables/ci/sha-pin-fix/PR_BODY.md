## Summary

Adds a verified, ready-to-apply repair for the unresolvable GitHub Actions SHA pins in `.github/workflows/ci.yml` and `.github/workflows/test-and-coverage.yaml`.

The Fig GitHub App installation on this repository lacks the `workflows` permission, so a push touching `.github/workflows/` is rejected at the remote:

```
! [remote rejected] ci/fix-sha-pins -> ci/fix-sha-pins
  (refusing to allow a GitHub App to create or update workflow
   `.github/workflows/ci.yml` without `workflows` permission)
```

This PR therefore ships the fix as a patch plus an applying script, so it can be landed from a machine that holds the permission. **Nothing under `.github/workflows/` is modified by this PR.**

## Key Points

- **Root cause of the red checks.** Every action ref in the two files is pinned to a 40-hex commit that does not exist upstream. Jobs die during action resolution, before any real work:
  `##[error]Unable to resolve action … unable to find version …`
  This is the cause of the pre-existing `Python 3.11`, `Python 3.12` and `lint` failures on `main` — unrelated to any individual PR.
- **Minimal fix.** Only the SHA in each `uses:` ref is replaced. Indentation, job names, `env` blocks, `run` steps and comments are untouched.
- **13 refs in `ci.yml`** across 4 jobs (`lint`, `test`, `security`, `build`); **4 refs in `test-and-coverage.yaml`**. Trailing version comments in the latter were corrected to match the new pins.
- **Self-checking script.** `apply.sh` refuses to continue if the patch does not apply cleanly, if either file stops parsing as YAML, or if any unpinned `@vN` ref remains.

| Action | Old (404) | New | Tag |
|---|---|---|---|
| `actions/checkout` | `f548e57c…` | `11d5960a…` | v4.4.0 |
| `actions/setup-python` | `5fda3b9c…` | `a26af69b…` | v5.6.0 |
| `codecov/codecov-action` | `eaaf46c7…` | `b9fd7d16…` | v4.6.0 |
| `docker/build-push-action` | `4a13b6b0…` | `10e90e36…` | v6.19.2 |
| `docker/login-action` | `74a5d146…` | `c94ce9fb…` | v3.7.0 |
| `github/codeql-action` | `977e6ce4…` | `faaca9a8…` | v3.38.0 |
| `actions/upload-artifact` | `65462800…` | `ea165f8d…` | v4.6.2 |

## Expected Result

- `deliverables/ci/sha-pin-fix/` on `main` containing the patch, an applying script, and a README.
- Running `./apply.sh --apply` from a permissioned machine lands the workflow fix and opens its own PR.
- After that PR merges, `Python 3.11`, `Python 3.12` and `lint` go green, since their failures were purely action resolution.

## Validation

- `git apply --check` against a fresh `main` clone — **clean, no conflicts**.
- Every replacement SHA confirmed to carry its expected release tag (`v4.4.0`, `v5.6.0`, `v4.6.0`, `v6.19.2`, `v3.7.0`, `v3.38.0`, `v4.6.2`).
- Both patched files parse as YAML with the expected jobs.
- Zero unpinned `@vN` refs remain after applying the patch.
- Discriminator test performed: a probe commit touching only a non-workflow file pushed successfully, while the same branch carrying the workflow change was refused — confirming the block is the workflow path, not credentials or branch protection.

## Operational Impact

None at merge time — this PR adds files under `deliverables/` only. No workflow, source, test or dependency change. The workflow fix activates only when someone runs `apply.sh`.

## Risk

Low.

- **Patch drift:** if `.github/workflows/ci.yml` or `test-and-coverage.yaml` changes before the patch is applied, `git apply --check` will fail and `apply.sh` will stop rather than apply a partial change. Re-derive the patch at that point.
- **Not auto-applied:** this bundle does nothing on its own. Someone with `workflows` permission must run it.
- **Version-comment correction:** the comments in `test-and-coverage.yaml` were updated alongside the pins. This is cosmetic but intentional, so the comment matches the pinned version.

## Rollback

Nothing to roll back at merge time. If `apply.sh` has already been run, revert its PR:

```bash
git revert <merge_sha> && git push origin main
```

## Notes

- Alternative considered and rejected: adding the `workflows` permission to the Fig App installation. It is an owner-level action and does not remove the need for the fix itself.
- Separately, `codeql.yml` sits at the repository root (outside `.github/workflows/`), so GitHub never runs it. Its YAML is also malformed at line 34 and it uses unpinned `@v3` refs. **It should not simply be moved into `.github/workflows/`** — the repo already has two active dynamic CodeQL workflows (`CodeQL`, `CodeQL - Code Quality`), and adding an advanced workflow alongside a default setup causes GitHub to reject the analysis. That needs a deliberate decision, not a move.
