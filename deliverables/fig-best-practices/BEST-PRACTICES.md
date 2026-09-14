# FIG / hellofig.ai Best Practices — the standard

The rules this repository is measured against, in prose. Every claim here is
enforceable: the machine-readable form lives in
[`policy/fig-best-practices.yaml`](./policy/fig-best-practices.yaml), and
[`quality_gate.py`](./quality_gate.py) checks a project against it. If the two
ever disagree, the policy wins and this document is wrong.

Version **1.0.0** · policy `verified_on` **2026-09-14**

## The six layers

Each layer is owned by a role, and later layers assume earlier ones hold. A
broken layout makes design review meaningless; a leaked credential makes
performance work pointless.

| Layer | Owner role | What it guarantees |
|-------|-----------|--------------------|
| `01-structure` | developer | Predictable layout, so nobody has to search |
| `02-design` | designer | Values come from tokens; contrast floor is met |
| `03-security` | security | No committed secrets; least privilege |
| `04-performance` | performance | Assets stay inside budget |
| `05-team` | reviewer | Changes are reviewable; roles are declared |
| `06-deployment` | deployment | A release has a rollback path before it ships |

## 1. Structure

`README.md` and `BEST-PRACTICES.md` exist at the root, and any directory the
policy lists under `rules.structure.required_dirs` is present. Structure is a
gate criterion because agents navigate by it: a conventional layout is what
lets an assistant find the right file without reading the whole tree.

```
project/
├─ README.md
├─ BEST-PRACTICES.md
├─ design/design-tokens.json
├─ integrations/*.integration.yaml
├─ agents/               # one instruction file per role
├─ src/
├─ tests/
├─ BACKUP.md
└─ DEPLOYMENT.md
```

## 2. Design system

Colour, spacing, radius, type, motion, and breakpoints are declared once in
`design/design-tokens.json`. Source files reference tokens; they do not inline
values.

Contrast is **computed, not asserted**. Every pair in `$contrastPairs` is
evaluated against the WCAG 2.1 relative-luminance formula at the policy's
`contrast_floor` (4.5:1 for normal text). Change a token and the gate catches
it — that is the difference between a checklist and a gate.

Hard-coded colour literals in `src/` fail DESIGN, except for the neutral values
the policy allowlists (`#fff`, `#000`, `transparent`, `inherit`,
`currentColor`) and anything inside a comment.

## 3. Security

No credential material in the tree. The gate scans for AWS key ids,
OpenAI-style `sk-` keys, GitHub tokens, private-key blocks, Slack webhook URLs,
and credential-shaped assignments — each pattern reporting file and line, with
the matched value redacted before it is printed.

An environment file (`.env`, `.env.local`, `.env.production`) must not be
committed. `.env.example` and its variants are allowlisted and are the correct
place to document a variable.

Integrations reference secrets, never contain them: `secretRef` accepts
`env:NAME`, `vault:path`, or `none`. A literal value fails validation.

## 4. Performance

Images carry a size budget (`rules.performance.image_size_budget_kb`, default
250KB). Legacy formats — PNG, JPG, GIF — get a much smaller allowance (60KB),
because anything larger should be WebP, AVIF, or SVG. The rule is deliberately
unforgiving: an unoptimised hero image is the most common performance
regression and the cheapest to prevent.

## 5. Team workflow

At least one test file must match the policy's globs. Every role in the policy
must declare a `scope` naming a real layer, and every file in `agents/` must
declare its own `scope:` that resolves. A role with no scope is not a role; it
is an unowned decision waiting to happen.

## 6. Deployment

A release is not ready until the evidence exists:

- an approval record (`DEPLOYMENT.md` or `docs/deployment.md`)
- a backup record with a rollback path (`BACKUP.md`, `docs/backup.md`, `docs/rollback.md`)
- the required artifacts listed in the policy

Supply-chain pinning is part of this layer, not a separate concern: every
`uses:` in `.github/workflows/` must be a full 40-character commit SHA. A
floating tag (`@v4`) is a dependency you did not choose.

## The eight criteria

| Criterion | Fails when |
|-----------|-----------|
| STRUCTURE | required files or directories are missing |
| DESIGN | no token file, invalid hex, contrast below floor, hard-coded colour |
| SECURITY | a forbidden pattern matches, or an env file is committed |
| PERFORMANCE | an image is over budget, or a legacy format is oversized |
| TESTING | no test file matches the declared globs |
| PERMISSIONS | a role has no scope, or an agent file declares none |
| BACKUP | no backup record, or no rollback path |
| DEPLOYMENT | no approval record, missing artifact, or an action is not SHA-pinned |

Exit code `0` means every blocking criterion passed. Exit code `1` means route
the project to auto-fix.

## Working with agents

`agents/` holds one instruction file per role. Each names the layer it owns and
the rules it enforces, so an agent working on design does not silently make a
security decision.

## Corrections to the source guide

This document was derived from an internal best-practices write-up. Four of its
claims did not survive checking, and are recorded here rather than silently
dropped — `policy/fig-best-practices.yaml` carries the same list under
`corrections:`

- **`npx create-fig-app@latest` and `fig add-agent dola`** — you state both
  commands are real. They are kept, attributed to you, and marked `unverified`
  in the policy: this document does not assert them from its own evidence, and
  nothing here depends on them working.
- **Hard-coded `model="gpt-4o"`** — replaced with a config-supplied model id.
  Pinning one vendor's model contradicts the multi-model premise the same guide
  argues for, and dates immediately.
- **`https://docs.hellofig.ai/`** — host does not resolve. The official platform
  site is `https://hellofig.app/`.
- **`https://hellofig.ai/`** — a different domain from the official
  `hellofig.app` platform site.

## Using the gate

```bash
python quality_gate.py --root /path/to/project     # human-readable
python quality_gate.py --root . --json             # for CI
python quality_gate.py --list                      # criteria from the policy
python -m pytest tests -q                          # the test suite
```

Wire it into CI as a step:

```yaml
- name: FIG best-practices gate
  run: python deliverables/fig-best-practices/quality_gate.py --root . --json
```
