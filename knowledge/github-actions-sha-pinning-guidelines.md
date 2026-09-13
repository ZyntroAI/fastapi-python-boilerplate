---
title: "GitHub Actions SHA Pinning Guidelines"
description: "Pin every action to a verified commit SHA: why tags are unsafe, how to prove a SHA exists, and the workflow-file traps that fail before any job runs."
tags:
  - knowledge/github-actions
  - knowledge/security
  - knowledge/supply-chain
  - knowledge/ci
supabase_area: "Engineering / CI-CD"
doc_kind: "guideline"
status: "active"
owner: "Platform Engineering"
last_reviewed: "2026-09-14"
review_frequency: "Quarterly"
source: "GitHub official documentation"
---

GitHub Actions SHA Pinning Guidelines

## Purpose

Defines how to pin GitHub Actions to immutable commits, and how to prove a pin is
real rather than merely SHA-shaped. Written after an audit that found ten refs
which passed every pattern check and still failed to resolve.

## Scope

All workflow files under `.github/workflows/`, including reusable workflows and
composite actions referenced with `uses:`.

## Why a tag is not a pin

An action reference is `owner/repo@ref`. When `ref` is a tag such as `v4`, the
tag is mutable: the repository owner can move it to a different commit, so the
code that runs can change without any change in this repository [1]. Branch refs
(`@main`) are worse, since they move on every push.

Both the GitHub security hardening guidance [2] and the workflow syntax reference
[3] recommend a full-length commit SHA as the only immutable reference. A commit
SHA names one exact tree; it cannot be retargeted.

## A SHA-shaped string is not a pin

This is the failure mode that pattern-based checks miss. A ref can be 40
hexadecimal characters and not exist at all — fabricated, truncated, or copied
from a different repository's history. GitHub reports this only when the workflow
starts, as `Unable to find version` during `Set up job`, before the first step
runs [4].

Consequences of that timing:

- the workflow fails with **zero** steps executed, so the failure looks
  unrelated to the diff that introduced it
- every pull request in the repository shows red checks, whether or not it
  touches workflows
- fixing a tag (`@v4` → `@<sha>`) into another fabricated value changes nothing

The rule: **a pin is verified only when GitHub confirms the commit exists in that
action's own repository.**

## How to verify a pin

Query the commit in the action's repository and require a 200:

```bash
gh api repos/actions/checkout/commits/b4ffde65f46336ab88eb53be808477a3936bae11 --jq .sha
```

A commit that does not exist returns 404 or 422. Two practical notes:

- **Rate limits.** The unauthenticated REST API allows 60 requests per hour [5].
  Use an authenticated client, or the HTML commit URL
  (`https://github.com/<owner>/<repo>/commit/<sha>`), which answers 200 for a real
  commit and 404 otherwise and is not subject to that limit.
- **Subdirectory actions.** `owner/repo/subdir@sha` lives in `owner/repo`. Resolve
  and verify against the first two path segments only; querying
  `owner/repo/subdir/commit/<sha>` 404s even for a real commit and yields a false
  "fake" verdict.

## Annotated tags must be dereferenced

When resolving a tag to a SHA, GitHub may return a **tag object** rather than a
commit. Pinning to a tag object fails to resolve at run time. The commit is the
dereferenced ref:

```bash
git ls-remote --tags https://github.com/actions/checkout.git 'refs/tags/v4^{}'
```

Dereferencing happens automatically through the commits API [5]; with
`ls-remote` the `^{}` suffix is required [6].

## Prefer the version already in use

When a ref carries no version information, pin it to the SHA already used for
that same action elsewhere in the repository, rather than to the latest release.
Silently advancing a major version inside a security fix changes behaviour the
author did not ask to change.

If a comment names a version that does not exist (for example a tag that was
never cut), pin to the nearest real tag and correct the comment. Do not invent a
value to match the comment.

## Workflow-file traps that fail before any job runs

**`on` parses as a boolean.** YAML 1.1 resolves the bare key `on` to `True` [7],
so a validator checking `"on" in config` reports every valid workflow as missing
its trigger. Accept both spellings.

**Block scalars need their whole body indented.** Inside `run: |`, every line —
including a heredoc terminator — must be indented at least as far as the block
[3]. YAML then strips that common indent, so the shell still receives the
original text. A heredoc written at column 0 makes the file unparseable, and the
workflow never appears in the Actions tab.

**Pasted prose around a workflow.** Text prepended or appended to a workflow body
makes the file invalid. Keep the mapping and drop everything outside it.

**Concatenated documents.** Two `jobs:` blocks in one file, usually from a
copy-paste that lost its separator, is not a valid workflow.

## Container images

The same mutability argument applies to container images. Pin `image: owner/name`
by digest (`@sha256:...`) rather than by tag, so the exact image cannot be
replaced under the reference [2].

## Unifying versions is a separate decision

Two workflows legitimately using different versions of one action is normal.
Replacing broken pins with real ones and unifying versions across working lines
are different changes with different blast radii; report the mixing rather than
folding it into a repair.

## Verification checklist

1. Every `uses:` carries a 40-character lowercase hex ref
2. Every ref resolves to a 200 in **that action's** repository
3. No `@vN`, `@main`, placeholder, or `<...>` ref remains
4. Every workflow file parses as a single YAML document
5. Line endings preserved — check `CRLF` counts before and after, or a
   `read_text()`/`write_text()` round trip will rewrite the whole file
6. A diff review confirms only intended lines changed

การอ้างอิง:

[1] About custom actions | GitHub Docs https://docs.github.com/en/actions/sharing-automations/creating-actions/about-custom-actions
[2] Security hardening for GitHub Actions | GitHub Docs https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
[3] Workflow syntax for GitHub Actions | GitHub Docs https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
[4] Troubleshooting workflows | GitHub Docs https://docs.github.com/en/actions/how-tos/troubleshoot-workflows
[5] REST API endpoints for commits | GitHub Docs https://docs.github.com/en/rest/commits/commits
[6] git-ls-remote documentation | Git SCM https://git-scm.com/docs/git-ls-remote
[7] YAML 1.1 specification — Boolean language-independent types | yaml.org https://yaml.org/type/bool.html
[8] Events that trigger workflows | GitHub Docs https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
[9] Permissions for the GITHUB_TOKEN | GitHub Docs https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication
[10] Managing GitHub Actions settings for a repository | GitHub Docs https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
