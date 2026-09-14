# fig-best-practices

The FIG / hellofig.ai best-practices standard as an **executable deliverable** —
not a document people read and forget, but a policy file that CI and agents
both enforce.

The prose standard is in [`BEST-PRACTICES.md`](./BEST-PRACTICES.md). This file
covers the machinery.

## What this is

Three coupled artifacts, so the words and the enforcement cannot drift:

| Artifact | Path | Consumer |
|----------|------|----------|
| Prose standard | `BEST-PRACTICES.md` | humans |
| Machine policy | `policy/fig-best-practices.yaml` | CI, agents |
| Executable gate | `quality_gate.py` + `figbp/` | pipeline |

The six layers (`01-structure` … `06-deployment`) and the eight criteria are
defined **once**, in the policy file. The document and the gate both derive from
it. Ask the policy what the rule is — never a hard-coded constant.

## Layout

```text
fig-best-practices/
├── BEST-PRACTICES.md              prose standard
├── policy/
│   └── fig-best-practices.yaml    single source of truth
├── design/
│   └── design-tokens.json         centralised tokens + contrast pairs
├── integrations/
│   ├── integration.schema.json    contract schema
│   └── example.integration.yaml   worked example
├── agents/                        one instruction file per role
│   ├── README.md                  role table + shared contract
│   ├── developer.md               scope: 01-structure
│   ├── designer.md                scope: 02-design
│   ├── security.md                scope: 03-security
│   ├── performance.md             scope: 04-performance
│   ├── reviewer.md                scope: 05-team
│   └── deployment.md              scope: 06-deployment
├── figbp/                         the gate engine
│   ├── policy.py                  load + validate the policy, glob matching
│   ├── tokens.py                  token validation + real WCAG contrast math
│   ├── secrets.py                 credential scanning (redacting)
│   ├── integrations.py            contract validation
│   └── gate.py                    the eight criteria
├── quality_gate.py                CLI entry point
├── scripts/
│   └── make_fixtures.py           generates the example image fixtures
├── tests/                         the suite
├── ci/
│   └── quality-gate.yml           workflow template to copy into .github/
└── examples/
    ├── clean-project/             passes 8/8
    └── broken-project/            fails 7/8, deliberately
```

## Use it

```bash
# Run the gate on any project directory
python quality_gate.py --root /path/to/project

# Machine-readable output for CI
python quality_gate.py --root . --json

# List the criteria straight from the policy
python quality_gate.py --list

# Optional: fail on advisory findings too
python quality_gate.py --root . --fail-on-advisory

# The suite
python -m pytest tests -q
```

Exit code `0` = every criterion PASS, safe to deploy. `1` = at least one FAIL,
route to auto-fix. `2` = the policy itself is missing or malformed — a broken
policy is a hard error, never a silent pass.

## The eight criteria

| Criterion | What fails it |
|-----------|---------------|
| STRUCTURE | missing `README.md` / `BEST-PRACTICES.md`, missing declared directory |
| DESIGN | no token file, invalid hex, contrast below the declared floor, hard-coded colour in `src/` |
| SECURITY | any forbidden pattern match (AWS keys, `sk-` keys, `ghp_` tokens, private keys, credential assignments), committed `.env` |
| PERFORMANCE | raster images over the size budget, legacy formats over their smaller allowance |
| TESTING | no test file matches the declared globs |
| PERMISSIONS | undeclared role, role without a scope, `agents/` file with no `scope:` |
| BACKUP | no backup record, no rollback path |
| DEPLOYMENT | missing approval record or required artifact, an action not SHA-pinned |

## Design notes worth knowing

**Contrast is computed, not asserted.** `figbp/tokens.py` implements the WCAG
2.1 relative-luminance formula, so the ratio is derived from the two colours
rather than trusted from a comment. `#767676` on white is the canonical
boundary case at 4.54:1, and the tests pin it.

**Secrets are redacted before they are printed.** Every finding reports file and
line with the matched value masked to a four-character prefix. A gate that
echoes the credential it found has moved the leak, not fixed it.

**Glob matching handles `**` correctly.** `fnmatch` treats `**/*.py` as a
single-segment pattern, which silently under-reports. `glob_to_regex` in
`figbp/policy.py` expands it properly, and the tests cover the difference.

**The broken example is the important one.** A gate that only ever passes
proves nothing. `examples/broken-project` commits a credential, hard-codes a
colour, drops the tests' neighbours, and leaves an action unpinned — each defect
is asserted against the criterion that must catch it, naming file and line.

## Verification

```text
examples/clean-project    8/8 PASS  (exit 0)
examples/broken-project   1/8 PASS  (exit 1)  — TESTING passes; the rest fail by design
tests/                    68 passed
```

## Wiring it into CI

The GitHub App on this org lacks the `workflows` scope, so the workflow lives at
`ci/quality-gate.yml` inside this deliverable rather than at the repository
root. Copy it to `.github/workflows/`, or add the gate as a step in an existing
job:

```yaml
- name: FIG best-practices gate
  run: python deliverables/fig-best-practices/quality_gate.py --root . --json
```

## Extending it

1. Add the rule to `policy/fig-best-practices.yaml`.
2. Add the matching check in `figbp/gate.py` and register it in `CRITERIA`.
3. Add a criterion by listing it under `quality_gate.criteria` — the gate reads
   its list from the policy, so it is picked up automatically. A criterion with
   no implementation is reported as such rather than passing silently.
4. Cover it in `tests/test_gate.py`, ideally against one of the example
   projects.

## Corrections carried from the source guide

Four claims in the original write-up did not survive checking. They are recorded
in the policy under `corrections:` and explained in `BEST-PRACTICES.md` rather
than quietly removed — including two commands the user confirms are real, which
are kept and marked `unverified` because this deliverable has no evidence of its
own for them.

## Requirements

Python 3.10+ and PyYAML. Nothing else for the gate itself; `pytest` for the
suite. If `jsonschema` is installed the integration tests cross-check the
built-in validator against it (and skip if it is absent).

## Licence and ownership

Internal ZyntroAI standard. Every role in `agents/` is scoped to exactly one
layer; changes to a layer belong to that layer's owner.
