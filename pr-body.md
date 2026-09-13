## 🚀 Agent Task Skills + Merge Protection

Additive-only PR. **No existing file is modified or deleted** (verified: `git diff --cached --name-status` returns additions only).

### 🧠 Agent Task Skills — `knowledge/agents/`

Six composable, dependency-free skills covering a unit of work end to end. Each ships as `SKILL.md` (contract) + `main.py` (logic) + `tests/` (pytest), with a machine-readable `manifest.yml` index.

| Skill | Responsibility | Entry point |
|---|---|---|
| `task-master` | Decompose a goal, order by dependency, refuse cycles | `TaskMaster.plan()` |
| `result-orchestrator` | Collect outcomes, apply quality gates, reduce to a verdict | `ResultOrchestrator.aggregate()` |
| `milestone-tracker` | Grade timeline health from slip against schedule | `MilestoneTracker.health()` |
| `blocker-resolver` | Classify obstacles and route escalations | `BlockerResolver.triage()` |
| `handoff-coordinator` | Gate a handoff on completeness | `HandoffCoordinator.receipt()` |
| `summary-reporter` | Render an executive update that leads with decisions | `SummaryReporter.report()` |

**Tests: 40 passed** (`python -m pytest knowledge/agents -q`)

Design rules: deterministic (no clocks, no randomness); explicit failure (a cycle, an unknown dependency, an unknown status, or an incomplete handoff is rejected, never tolerated); no hidden state.

### 🛡️ Merge Protection

- **`.gitattributes`** — `merge=union` for documentation so two branches appending to the same note cannot conflict; strict `merge=text` for code; `merge=binary -diff` for lock files; normalised LF endings; binary asset handling.
- **`.github/CODEOWNERS`** — review routing for `knowledge/**`, `.github/workflows/**`, `security/**`, `deliverables/**`, and app code. Paths changed by this PR are owned by `@ZyntroAI`.
- **`.github/merge_rules.json`** — the merge policy as machine-readable config: `MERGE_COMMIT` default, squash/rebase disallowed on `main`, 2 approvals, stale-review dismissal, required checks, protected paths, additivity rules, and delete protection.

### ⚠️ What is *not* in this PR

- **`protect-merge.yml`** — the CI enforcement workflow is deliberately **excluded**. The `fig-ai-agent` GitHub App on this repo does not hold the `workflows` permission, and GitHub rejects an entire push at the tree level if any commit touches `.github/workflows/`. The file is delivered separately as a drop-in for manual installation. `merge_rules.json` documents the checks it declares (`protect-merge`, `CI`, `secret-scan`); the workflow itself must be added before those checks can gate.
- **Supabase documentation** — the six guides named in the original brief (SSO signing, OAuth apps, audit logs, audit log drains, legal documents, feature previews) **already exist on `main`** as `knowledge/supabase-*.md`, merged 2026-09-13 with front matter, sha256 hashes, `knowledge/manifest.yml`, and a README index. Re-adding them would create duplicates.
- **`CONTRIBUTING.md` / `.github/PULL_REQUEST_TEMPLATE.md`** — specified in the brief but **already present** (212 and 60 lines respectively). Shipping the brief's versions would have overwritten them, which contradicts this PR's own no-replacement policy.

### ✅ Verification

- All changes are pure additions; `main` is untouched.
- `manifest.yml` and `merge_rules.json` parse cleanly (YAML/JSON validated).
- 40/40 skill tests pass.
- No secrets or credentials.
