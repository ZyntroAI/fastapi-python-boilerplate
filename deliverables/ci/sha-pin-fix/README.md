# Action SHA-pin repair — `fastapi-python-boilerplate`

Ready-to-apply repair for the unresolvable action SHA pins in
`.github/workflows/ci.yml` and `.github/workflows/test-and-coverage.yaml`.

## Why this is a patch and not a PR

The Fig GitHub App installation on `ZyntroAI/fastapi-python-boilerplate` does not
carry the **`workflows`** permission. Any push that touches
`.github/workflows/` is rejected at the remote:

```
! [remote rejected] ci/fix-sha-pins -> ci/fix-sha-pins
  (refusing to allow a GitHub App to create or update workflow
   `.github/workflows/ci.yml` without `workflows` permission)
```

A discriminator check confirmed this precisely: a probe commit touching only a
non-workflow file was accepted, while the same push including the workflow
change was refused. The block is the workflow path, not credentials or branch
protection.

So the fix ships as a verified patch plus an applying script. Run it from a
machine (or token) that has `workflows` permission.

## The bug

Every action reference in these two files is pinned to a 40-hex commit that
**does not exist upstream**. The result is that each job dies during action
resolution, before any real work runs:

```
##[error]Unable to resolve action `actions/checkout@f548e57c3d3c42e288026812cd22362661c4e8d4`,
unable to find version `f548e57c3d3c42e288026812cd22362661c4e8d4`
```

This is the root cause of the pre-existing red `Python 3.11`, `Python 3.12` and
`lint` checks on `main`. It is unrelated to any individual PR.

## The fix

Replace **only the SHA** in each `uses:` ref. Indentation, job names, env
blocks, `run` steps and comments are left byte-for-byte untouched.

| Action | Old (404) | New | Tag |
|---|---|---|---|
| `actions/checkout` | `f548e57c…` | `11d5960a…` | v4.4.0 |
| `actions/setup-python` | `5fda3b9c…` | `a26af69b…` | v5.6.0 |
| `codecov/codecov-action` | `eaaf46c7…` | `b9fd7d16…` | v4.6.0 |
| `docker/build-push-action` | `4a13b6b0…` | `10e90e36…` | v6.19.2 |
| `docker/login-action` | `74a5d146…` | `c94ce9fb…` | v3.7.0 |
| `github/codeql-action` | `977e6ce4…` | `faaca9a8…` | v3.38.0 |
| `actions/upload-artifact` | `65462800…` | `ea165f8d…` | v4.6.2 |

`ci.yml` has 13 refs across 4 jobs (`lint`, `test`, `security`, `build`);
`test-and-coverage.yaml` has 4 refs. In `test-and-coverage.yaml` the trailing
version comments were also corrected to match the new pins.

## Usage

```bash
cd deliverables/ci/sha-pin-fix

./apply.sh            # dry run: clone main, verify the patch applies, stop
./apply.sh --apply    # apply, verify YAML, commit, push, open the PR
```

The script refuses to continue if the patch does not apply cleanly, if either
file stops parsing as YAML, or if any unpinned `@vN` ref remains.

## Verification already performed

- `git apply --check` against a fresh `main` clone — **clean, no conflicts**.
- Every replacement SHA confirmed to carry its expected release tag.
- Both files parse as YAML with the expected jobs:
  `ci.yml` → `lint`, `test`, `security`, `build`;
  `test-and-coverage.yaml` → `test`.
- Zero unpinned `@vN` refs remain in either file.

## After the merge

`Python 3.11`, `Python 3.12` and `lint` should go green — the failures were
purely action resolution. If any of them still red, the remaining cause is the
job body rather than the pins, and should be read from the fresh job logs.
