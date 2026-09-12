# fig-best-practices

The Fig / hellofig.ai best-practices standard as an **executable deliverable** —
not a document that people read and forget, but a policy file that CI and agents
both enforce.

## What this is

Your `BEST-PRACTICES.md` checklist, promoted into three coupled artifacts:

| Artifact | Path | Consumer |
|----------|------|----------|
| Prose standard | `BEST-PRACTICES.md` | humans |
| Machine policy | `policy/fig-best-practices.yaml` | CI, agents |
| Executable gate | `quality_gate.py` + `figbp/` | pipeline |

The six layers (`01-structure` … `06-deployment`) are defined **once**, in the
policy file. The document and the gate both derive from it, so they cannot drift.

## Layout

```text
fig-best-practices/
├── BEST-PRACTICES.md              prose standard, 10 sections + agent extension
├── policy/
│   └── fig-best-practices.yaml    single source of truth
├── design/
│   └── design-tokens.json         centralized tokens, with accessibility floor
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
│   ├── policy.py                  load + validate the policy
│   ├── tokens.py                  token validation + real WCAG contrast math
│   ├── secrets.py                 credential scanning
│   ├── integrations.py            contract validation
│   └── gate.py                    the eight criteria
├── quality_gate.py                CLI entry point
├── tests/                         32 tests
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

# The test suite
python -m pytest tests -q
```

Exit code `0` = every criterion PASS, safe to deploy. Exit code `1` = at least
one FAIL, route to auto-fix.

## The eight criteria

| Criterion | What fails it |
|-----------|---------------|
| STRUCTURE | missing `README.md` / `BEST-PRACTICES.md`, incomplete `agents/` |
| DESIGN | no token file, invalid hex, contrast below the declared floor, hard-coded colours in `src/` |
| SECURITY | any forbidden pattern match (AWS keys, `sk-` keys, `ghp_` tokens, private keys, credential assignments), committed `.env` |
| PERFORMANCE | raster images over the size budget, images in a non-modern format |
| TESTING | no test files found |
| PERMISSIONS | undeclared role, agent without a declared scope |
| BACKUP | no backup record, no rollback path |
| DEPLOYMENT | production requirements unmet, no approval recorded |

## Verification

```text
examples/clean-project    8/8 PASS  (exit 0)
examples/broken-project   1/8 PASS  (exit 1)
```

The broken example is intentional: it commits a credential, hard-codes a colour,
and drops the tests, backup, and deployment evidence. The gate catches each one
and names the file and line — which is the whole point of having a gate rather
than a checklist.

## Wiring it into CI

The GitHub App on this org lacks the `workflows` scope, so the workflow template
lives at `ci/quality-gate.yml` inside this deliverable rather than at the
repository root. Copy it to `.github/workflows/` once that permission is
available, or run the gate as a step in an existing job:

```yaml
- name: FIG-BEST-PRACTICES gate
  run: python deliverables/fig-best-practices/quality_gate.py --root . --json
```

## Extending it

Add a rule by editing `policy/fig-best-practices.yaml` and the matching check in
`figbp/gate.py`. Add a criterion the same way — the gate reads its list from the
policy, so a new entry in `quality_gate.criteria` is picked up automatically.
