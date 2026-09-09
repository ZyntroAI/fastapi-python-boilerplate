# Release Guide

How this repository prepares, versions, and ships releases. Every change flows
through a reviewed PR to `main` first (see `CONTRIBUTING.md`); releases are
cuts from `main` after the changelog is updated.

## Versioning

Semantic Versioning (`MAJOR.MINOR.PATCH`). The repo currently tracks no
published package version — releases are GitHub Releases/tags on `main`.
- **MAJOR** — breaking changes (title contains `breaking`).
- **MINOR** — new features in a backwards-compatible way.
- **PATCH** — backwards-compatible bug fixes.

## Release flow

1. **Merge changes to `main`** through reviewed PRs (quality gates in
   `CONTRIBUTING.md`).
2. **Update `CHANGELOG.md`** under the current date section, noting each merged
   PR (`- **PR #N** — summary`). Keep it a faithful record of what actually
   merged.
3. **Cut the release** from a clean `main`:
   - Open a release PR using the template in
     [`deliverables/gh-devops-toolkit/pr-templates/release.md`](deliverables/gh-devops-toolkit/pr-templates/release.md)
     (labelled `release`).
   - The PR states the version, the changelog highlights included, any
     migration/breaking changes, and the verification checklist.
4. **Merge and tag** — squash-merge the release PR, then create an annotated
   tag on `main` (`git tag -a v1.2.0 -m "v1.2.0"`), and push the tag.
5. **Draft the GitHub Release** from the changelog section for that version.

## Automated label → section mapping

`.github/workflows/release_drafter.yaml` auto-labels PRs from their title, which
feeds the drafted release notes:

| Prefix (title)      | Release label     |
| ------------------- | ----------------- |
| `feat` / `feature:` | `feature`         |
| `fix:`              | `bug`             |
| `docs:`             | `documentation`   |
| `chore:`            | `chore`           |
| contains `breaking` | `breaking-change` |

Use conventional-commit PR titles so the drafter groups changes correctly and
breaking changes are visible.

## Verification before release

- [ ] CI green on `main`
- [ ] Tests pass
- [ ] `CHANGELOG.md` current and accurate
- [ ] Migration applied (if any)
- [ ] Breaking changes called out and versioned as `MAJOR`
- [ ] Tag + GitHub Release created from the changelog section

## Rollback

If a release is faulty, roll back via `git revert` of the offending merge(s) on
`main`, then cut a `PATCH` release. Never rewrite published history or retag an
existing release tag.
