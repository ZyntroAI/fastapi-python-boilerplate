# docs-verify — Documentation Drift Verifier

The README, `PROBLEMS.md` and `LICENSE` make claims a reader takes on trust:
how many deliverables exist, which paths are present, whether the workflows
parse, who holds the copyright. Those claims go stale the moment the tree moves
underneath them — a merge lands a new suite and the README keeps saying 24.

This checks the claims against the tree. Read-only, no network, standard
library only.

Version `0.1.0-origin`.

## Why this exists

Every fix in this repository's documentation has been a **number that drifted**:

| PR | Claim | Was | Is |
|----|-------|-----|----|
| #272 | `deliverables/` count | 24 | 25 |
| #273 | `docs/` file count | 31 | 32 |
| #278 | unpinned action refs | 66, then 23 | 60 |
| #278 | `P-009` | one id, two problems | split to `P-011` |

Each was found by hand, after the fact. Two of them — #272 and #273 — were
caused by a *concurrent merge* landing while the fix was in flight, which means
the same drift can happen again the day after any hand-fix. A number written in
prose has no way to notice it is wrong.

This tool is that notice.

## What it checks

| Check | Against |
|-------|---------|
| deliverables count | the number the README declares, vs `deliverables/*/` |
| every deliverable named | each directory appears as a `` `name` `` in the README |
| docs count | the README's declared count, vs `find docs -type f` |
| workflow count | the README's declared count, vs `.github/workflows/*` |
| README paths resolve | backticked `dir/file` claims actually exist |
| README core sections | `## Tests`, `## Deliverables`, `## License` survive edits |
| no fabricated draft | the invented `Origin Branch Strategy` heading is absent |
| LICENSE | no `[placeholder]` brackets; a holder is named |
| package.json | parses, and declares a `license` |
| workflows parse | each file is valid YAML — lists the broken ones by name |
| action pin split | reports `pinned/total` and the unpinned remainder |
| problem ids unique | no `P-00N` used by two entries |
| date sections | unique, and newest-first |
| date order | sections descend |

The point is the comparison, not the number: a count is checked against **what
the README itself declares**, so the check survives the tree legitimately
changing and fails only on genuine drift. A count written in prose (*"Five of
the eleven workflow files"*) is parsed too, including the spelled-out form.

## Use

```bash
python scripts/verify_docs.py            # human output, exit 1 on drift
python scripts/verify_docs.py --json     # machine-readable
python scripts/verify_docs.py --root .   # explicit repo root
python -m pytest tests/ -q               # the suite
```

Exit code is `0` when every non-skipped check passes, `1` otherwise — usable as
a CI gate or a pre-commit hook.

## Design notes

**Fixtures, not the live repo.** The test suite builds synthetic trees in
`tmp_path`, so it cannot start failing because an unrelated merge changed a
count. The live repository is exercised by the CLI instead.

**Meta headings are not duplicates.** `### P-001 / P-002 — re-verified today`
names two ids at once; it is a re-verification notice, not a second `P-001`
entry. The id check requires the em dash after the id, so only real entry
headings count.

**PyYAML is optional.** Without it the workflow-parse checks report `skip`, not
`fail` — a missing dev dependency should not read as a repository defect.

## Layout

```text
deliverables/docs-verify/
├── README.md
├── SKILL.yaml
├── package.json
├── .gitignore
├── src/docs_verify.py            engine — Report, Check, verify(), render()
├── scripts/verify_docs.py        CLI
└── tests/test_docs_verify.py     17 tests over synthetic fixtures
```
