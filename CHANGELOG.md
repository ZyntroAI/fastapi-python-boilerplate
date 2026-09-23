# Changelog

All notable changes to this repository. Dates are UTC.

Open problems and known blockers are tracked separately in
[`PROBLEMS.md`](./PROBLEMS.md), using the same date sections.

## [2026-09-23]

### Added

- **pg_trgm typo-tolerant search — runnable SQL test script + Thai guide.**
  `deliverables/pg-trgm-typo-tolerant-search/` adds an 8-section, re-runnable
  SQL script covering extension config, `similarity()`, the `%` operator,
  threshold tuning, GIN (`gin_trgm_ops`) indexing, and
  `word_similarity`/`strict_word_similarity`, closing with 12 self-checking
  assertions. Verified on PostgreSQL 17: 12 passed / 0 failed, and a second
  run on the same database is clean. `README.md` explains each section in Thai.
  Motivation: a Fig Search query on pg_trgm returned "No results captured"
  because the Search tool hit its usage limit — not because the topic was
  absent — so this suite tests trigram search directly in PostgreSQL instead.
  Three findings are documented: `LOAD 'pg_trgm'` is required for a re-runnable
  script (the GUCs are not registered otherwise); small tables Seq-Scan by cost,
  not because the index is broken; and `similarity()` already ignores case and
  leading/trailing whitespace, so what actually moves the score is inner
  whitespace and accents.
- **Workflow repair — SHA-pinning + YAML integrity.**
  `deliverables/workflow-repair/` fixes the defects that make every CI run in this
  repository fail at the `Set up job` step, before any checkout or test executes.
  Four workflow files were not parseable YAML (a stray `;` in `secret-scan.yml`, an
  unindented block scalar in `Auto-Index-Sync.yml`, 87 lines of GitHub docs appended to
  `dependabot-automerge.yml`, and `test-suite.yml` wrapped in markdown); one file
  (`github-actions-autodebug-autorerun`) was a prose spec with no `.yml` extension, so
  GitHub never loaded it, and is renamed to `auto-debug-rerun.yml`; and 70 `uses:` refs
  across 10 files carried literal `<commit-sha>` placeholders, SHAs that 404 upstream,
  or floating tags, all rewritten to verified full-length commit SHAs.
  Verified: all 11 files parse as YAML (10 declare `jobs`; `release_drafter.yaml` is an
  autolabeler config, flagged in the README), 0 non-pinned refs remain, and the patch applies
  cleanly to a fresh clone of `main` with all 11 files byte-identical afterwards.
  Ships as a patch plus the fixed files, because root `.github/workflows/**` is
  push-blocked for the Fig App.

- **PR #328** — moved twelve stray markdown files to the path each one
  belonged at, and collapsed two duplicate registries. Nothing was rewritten:
  `git` records all twelve as `R100`, and the two deletions are byte-identical
  copies (`supabase.md` matched `docs/supabase.md`, `mcp-server.md` matched
  `docs/tools/mcp-server.md`) — `README.md` already linked the `docs/` copies, so
  the root ones were dead weight rather than a second source of truth. Landing
  points were chosen from evidence, not resemblance: `claude-rest-api.md` went to
  `docs/` because its own handoff document specifies that path. The larger find
  was inside `docs/README.md`, where ~38 KB of Enterprise Feature Stack material
  (Feature Manifest, Policy Schema, Deployment Config, README-ENTERPRISE) had been
  pasted onto the end of the index; it is now `docs/enterprise-feature-stack.md`,
  extracted char-exact — every payload line verified present — leaving the index
  an index again, with the newly-moved files listed. `deliverables/README.md` was
  a partial second copy of the list in `README.md` (15 of 19 names overlapped);
  it is now the single authoritative table of all 31 suites A–Z, and `README.md`
  points at it instead of repeating 27 names. Five declared counts were stale and
  are corrected against the tree: deliverables 27→31, docs 54→78, parsing
  workflows 6→5, skills 13→12; workflow files 11 was already right. Verified
  after: zero byte-identical duplicates remain (was two), and broken relative
  links are unchanged at 9 — all pre-existing, eight of them absolute GitHub web
  paths inside an imported document and one pointing at a file that never existed.
  Markdown only; no code or workflow file was touched.

- **PR #327** — `docs/RELEASE-AND-TEMPLATE-GUIDE.md`: consolidated the release-tag
  and template documentation that had been spread across twelve files into one
  guide. The tag half documents four separate paths rather than pretending there
  is one procedure: `RELEASE.md` (the official five-step annotated-tag flow),
  `.github/DEVELOPMENT.md` (the git-flow variant, in Thai, with the hotfix
  sequence and the merge-back step that is the one people skip),
  `docs/github-cli-gh-reference.md` (the `gh`-driven automation path, which tags
  the remote commit), and `deliverables/gh-devops-toolkit/pr-templates/release.md`
  (the PR half). The template half is the first written inventory of the
  repository's templates, including the fact that `.github/PULL_REQUEST_TEMPLATE/`
  holds nine and that `.github/ISSUE_TEMPLATE/` does not exist on `main` — stated
  because it had been assumed to exist. The overwrite-guard section records the
  three rules in `kernel/policy.yaml` as the machine-checkable form of the
  no-clobber policy, the three intents (create refused over an existing path,
  replace requiring exact-path approval, append allowed), and the CRLF-safe
  `appends:` settings. Two caveats are carried forward rather than smoothed over:
  never retag a published release, and CI on `main` is red at `Set up job`. Every
  claim was checked against the files on `main` before the branch was pushed.

## [2026-09-19]

### Added

- **PR #322** — `billing_manager.py` at the repository root: 436 lines of client,
  invoice and payment handling with an interactive console, optional `reportlab`
  PDF export and JSON persistence. It imports nothing from `app/`.
- **PRs #323–#326** — Dependabot, four bumps in one window: `vercel` 59.15.1 →
  59.17.0 (production deps), the npm dev-deps group (3 updates), the pip
  production-deps group (7 updates), the pip dev-deps group (4 updates).

## [2026-09-18]

### Changed

- **PR #320** — "Update ci.yml" replaced `.github/workflows/ci.yml`, 112 → 279
  lines. The replacement **does not parse as YAML** (`while scanning a simple
  key`), and every SHA pin in it is a commit that does not exist. A follow-up
  direct commit (`0685af6`) cut the file back to 87 lines; it now carries
  **13 `uses:` refs, all 13 fabricated, across 6 distinct SHAs** — up from 10
  refs across 3 before the change. Only that one file was touched.

  This is the file P-013 documents. Its counts were measured on the 112-line
  version and are now stale; the entry below has been refreshed.

## [2026-09-17]

### Added

- **PR #310** — `deliverables/dev-helpers/`: four stdlib-only tools for the
  friction points in automated GitHub work — `approval_doc`, `ci_workflow`,
  `perm_checker`, `pr_helper` — with 199 lines of tests, a `SKILL.md`, a Thai
  and an English guide, and a `manifest.json`. 13 files, no dependencies.
- **PR #313** — tracker: added `TASK-20260916-003`, recording a **live defect on
  `main`** — the tracker's own suite is red (`2 failed, 18 passed`).
- **PR #319** — `knowledge/manifest.yml`: recorded
  `github-actions-sha-pinning-guidelines.md`, which was already on `main` but
  missing from the manifest (`note_count` 6 → 7, `generated` 2026-09-13 →
  2026-09-16), and added the generated `knowledge_index.json` to `.gitignore`.

### Changed

- **PR #225** — `requirements.txt`, 6 lines. Two floors were raised past what
  exists on PyPI and four packages are now listed twice, so the file no longer
  resolves. See P-014.
- **PR #229** — `.vscode/`: a 35-line `launch.json` plus an `extensions.json`
  edit. The launch configuration added is .NET Core (`coreclr`), not Python.
  See P-015.

### Investigated

- **PRs #303 and #318** — merged this day, but their write-ups were appended to
  the [`[2026-09-16]`](#2026-09-16) section above rather than given a section of
  their own, where they still are. Listed here so the merge date is not lost:
  #303 added `eslint.config.mjs` and repaired `scripts.vite`; #318 landed
  `deliverables/cache-reduction-skill/` and an advisory CI gate.

  #318's edit to that section was a **replacement, not an append**: it removed
  PR #316's entry — the Chrome DevTools MCP production setup — and put its own
  in the same slot (17 lines out, 12 in). The guide it described,
  `docs/Chrome-DevTools-MCP-Production-Setup.md`, is still on `main`; only its
  changelog record is gone. See P-016.

## [2026-09-16]

### Added
- **Cache scan as an advisory CI gate** — the cache-footprint audit now runs on
  every push to `main`/`dev` and every PR to `main`, publishing its findings to
  the job summary and as a `cache-scan-report` artifact. The toolkit moves into
  `deliverables/cache-reduction-skill/` so the scan has a stable path to run
  from. Scope is `app/`. The job is deliberately advisory — every
  finding-bearing step is `continue-on-error: true` — because the scan reports
  three findings against the current tree, at least two of which are false
  positives (`setex` with a variable TTL, `@lru_cache` on a zero-argument
  getter), so a blocking gate would be red from its first run. Refs are pinned
  to the SHAs the repo's own repair set already verified.


### Fixed
- **Workflow repair install — handed off (TASK-20260916-004).** Every job on `main`
  still fails at `Set up job` in ~2–4s before a test runs, because the repaired
  workflow set has never been *installed* — `deliverables/ci/workflows-repaired/` sits
  on `main` unapplied. Installing it into a clean clone and running the repo's own gate
  gives `PASS — 11 workflows parse, are shaped correctly, and all 28 action refs are
  SHA-pinned`, versus four parse failures on `main`. The install cannot travel as a PR
  from the Fig App: a push touching `.github/workflows/**` is refused with
  `refusing to allow a GitHub App to create or update workflow … without workflows
  permission`, and that refusal lands before a PR can be opened. A non-workflow push to
  the same repo in the same session succeeded, so the block is the App-installation
  `workflows` permission — not credentials, not branch rules. Retried after the grant
  was reported: still refused, and an independent workflow-file write through the REST
  API returned `403 Resource not accessible by integration`, so the grant is not yet
  effective for this installation. Delivered instead as a non-workflow handoff —
  `docs/workflow-repair/` (verified patch + `HANDOFF.md`) and
  `scripts/install-workflow-repair.sh`, which installs, verifies, commits, pushes, and
  opens the PR in one command. No probe artifact was left on the repo.

- **PR #311** — merged the repaired workflow set to `main` and re-confirmed the
  push gate. The repair travels under `workflows-repaired/`: eleven workflow files
  that parse, with all 27 distinct `uses:` refs pinned to real 40-character commit
  SHAs. The wrong pins were the live failure — six of `main`'s refs were
  fabricated SHAs (`actions/checkout@f548e57c…`, `actions/setup-python@5fda3b9c…`,
  `github/codeql-action/*@977e6ce4…`, `actions/checkout@11bd7190…`), each a near-miss
  of the real commit, so GitHub rejected the workflow before any job ran while
  `lint.py` stayed green — it checks shape, not existence. Re-ran the push with the
  write grant approved: still `refusing to allow a GitHub App to create or update
  workflow`, so the missing `workflows` permission is the App-installation setting
  and not repository rules — a non-workflow push to the same repo succeeded in the
  same session. `deliverables/ci/workflows-repaired/install.sh` installs the set
  once a maintainer runs it; verified by installing into a clean tree, after which
  `verify_workflows.py --check-shas` reports PASS (11 workflows, 28 refs pinned).
  TASK-20260916-002.

- **PR #301** — fixed the SHA resolver in `deliverables/ci/verify_workflows.py`,
  which had been reporting every *correct* pin as non-existent. That is worse than
  having no check at all: it would fail CI on a healthy tree. Two independent bugs
  produced it. First, `git ls-remote <url> <sha>` is not a membership test —
  ls-remote takes ref *patterns*, so a raw SHA matches nothing and every pin looks
  fake; the fix lists a repository's refs once (cached) and tests membership.
  Second, `--refs` suppresses the peeled `<tag>^{}` lines, and for an annotated
  tag that line is the only place the *commit* hash appears — so a correctly
  pinned annotated tag was reported as fabricated. Dropping `--refs` resolves both
  lightweight tags (commit straight) and annotated tags (peeled) while a
  fabricated SHA still matches nothing. `deliverables/ci/test_verify_workflows.py`
  adds 11 cases covering both tag shapes, the `f548e57c…` fabrication that was
  live on `main`, a fabrication behind an action subpath, and a well-formed hash
  that names nothing. Found while installing the repaired workflows: after the
  repair, `--check-shas` still flagged four genuinely real pins.

- **Repaired workflows delivered for installation** — the GitHub App cannot push
  `.github/workflows/**` (no `workflows` scope: *refusing to allow a GitHub App to
  create or update workflow*), and that refusal happens at the transport layer,
  before a PR can even be opened. So the repaired set travels inside the PR under
  `deliverables/ci/workflows-repaired/` and is installed by a dry-run-by-default
  script. The repairs themselves: six of eleven workflow files could not be
  parsed or registered at all. `secret-scan.yml` carried a stray semicolon
  (`workflow_dispatch;`) that turned the rest of the line into another mapping
  key; `Auto-Index-Sync.yml` opened a shell heredoc whose body sat at column 0,
  ending the surrounding `run: |` block early; `dependabot-automerge.yml` had
  6,190 characters of GitHub UI documentation pasted onto its end;
  `test-suite.yml` was a chat reply — prose, a horizontal rule, the workflow
  inside a ```` ```yaml ```` fence, and 42 lines of trailing commentary;
  `github-actions-autodebug-autorerun` was a spec document saved without an
  extension; and `release_drafter.yaml` was not a workflow but a release-drafter
  config filed in the workflows directory, so GitHub registered it as an
  always-failing workflow. All 73 `uses:` refs are now pinned to real commits —
  60 had been left as tags or placeholders, including three SHAs that are
  well-formed but name nothing, which is why PRs failed at `Set up job` in two
  seconds while `lint.py` stayed green.

- **Three fabricated SHAs confirmed live on `main` — the cause of its red CI** —
  closes the open question from the PR #301 resolver work above, which proved
  `actions/checkout@f548e57c…` was a fabrication but could not say how much of
  the tree was affected. `main` has been failing since at least
  2026-09-15T20:31Z, and its `lint` job dies in *Set up job* after two seconds
  with

  ```
  ##[error]Unable to resolve action `actions/checkout@f548e57c…`, unable to find version `f548e57c…`
  ```

  Three distinct SHAs are well-formed 40-hex strings that name no real commit,
  used across 10 refs — all of them in `ci.yml`:

  | Ref | Refs |
  | --- | --- |
  | `actions/checkout@f548e57c3d3c…` | 4 |
  | `actions/setup-python@5fda3b9c7092…` | 3 |
  | `github/codeql-action/{init,autobuild,analyze}@977e6ce40888…` | 3 |

  So `ci.yml` is the one file that cannot start. The other nine workflows are
  unaffected by this, which is why the damage looked narrower than it is — every
  PR check routes through `ci.yml`. The repaired set under
  `deliverables/ci/workflows-repaired/` replaces all three with commits that
  resolve.

  This is a **different defect from P-002** despite looking identical in a diff.
  P-002 is unpinned *tags* (`@v4`), which the org's SHA-pinning policy rejects.
  These are pinned to nothing. The distinction matters because the two checks
  disagree: the org-policy check demands a pin and passes these, while GitHub
  executes the pin and fails them. An unpinned tag fails honestly and loudly; a
  fabricated SHA fails silently — which is exactly why PRs looked *blocked on
  CI* while the real cause was a pin pointing nowhere.

### Investigated

- **FIG-TASK-001 and FIG-TASK-002 are done; 003 was already done; 004 is blocked
  on `workflows` permission** — worked the four 🔴 items from the 2026-09-16
  FIG-TASK request (tracked as `TASK-20260916-001`). Two of the four needed no
  work, which is worth recording so the list can be trusted:

  **001** — `scripts.vite` was `">=6.4.3"`, a semver range where a command
  belongs, so `npm run vite` could never run. Set to `"vite"`.

  **002** — the fix the task list proposed would not have worked. It specifies
  `.eslintrc.cjs`, but the repo pins `eslint ^10.10.0`, which no longer reads
  `.eslintrc.*` at all — that file would have reproduced the identical failure.
  Added `eslint.config.mjs` (flat config) composing `@eslint/js`,
  `typescript-eslint`, `globals` and `eslint-config-prettier`, with per-file-type
  scoping so each plugin is registered in the same config object that uses it
  (a flat-config requirement, and the reason a hand-rolled spread throws
  *couldn't find plugin "typescript-eslint"*). `npm run lint` now exits 0.

  **003** — already done on `main` in `d2d29a4`. `.env` is not tracked, and
  `.gitignore` already covers `.env` and `.env.*`. No change needed.

  **004** — the repairs already exist on `main` under `deliverables/ci/`, so
  this is an install step, not missing work. Re-packaging them would have been a
  duplicate: the repaired set installs cleanly (`install.sh --apply`), after
  which `verify_workflows.py` passes — 11 workflows parse, 28 refs pinned, and
  every pin resolves to a real commit.

### Added

- **PR #308** — `deliverables/cross-repo-patch-suite/`: a suite for the three ways a patch
  breaks on the way between repositories, none of which is about the change
  itself. First, a Python text-mode round-trip normalises CRLF to LF, so a
  two-line append lands as a whole-file rewrite; the suite never decodes a file
  it will write back, and `verify_append` proves the pre-existing region survived
  byte for byte. Second, a CRLF file with no trailing newline passes
  `git apply --check` and *fails* `git am` with "patch does not apply" — the two
  commands disagree and the one that says OK is the one you run first. That is
  reproduced against real git in `tests/test_end_to_end.py`, with the
  byte-identical LF control passing both, and `audit_eol_risk` finds these files
  before the attempt. Third, an unquoted colon (`:x:`) is a YAML `ScannerError`
  and an `uses:` reference on a tag parses fine while still being mutable, so the
  parse check and the SHA-pin audit are kept independent. Includes `patchctl`
  (six subcommands), two helpers — `safe_append.py` and `fix_eol.py` — a
  `kernel/policy.yaml` holding every threshold, an overwrite guard that refuses a
  create over an existing file and requires exact-path approval to replace, and
  clean/broken fixtures written as exact bytes. Every mutating command is a dry
  run unless `--apply` is passed. 125 tests. TASK-20260916-001.

- **PR #306** — docs: refreshed `PROBLEMS.md` P-002, which had gone stale twice
  over: it described the fix as "76 refs pinned across 11 files" (never pushed)
  and carried 2026-09-14 evidence. Re-measured against `main` @ `6a7754d` —
  **13 pinned, 60 unpinned of 73 refs**, spread over 9 files and 25 distinct
  actions. The entry now names the commit the numbers were taken at, describes
  the fix as the verified patch pack rather than a branch, and carries a
  copy-pasteable snippet so the next reader re-measures instead of trusting a
  stored number. Earlier counts in that file (66, 60, 23) had each been
  overtaken as the tree moved.

- **PR #297** — docs: added `PROBLEMS.md` P-012, recording why `new-crystalcastle` PR #163 cannot merge. The dependabot bump to `react-dom@19.3.0` sits outside `@react-three/fiber@9.7.0`'s declared peer range (`>=19 <19.3`), so `npm ci` fails with `ERESOLVE`. Established by running `npm ci` on both refs rather than reading the log: `main` installs 703 packages (exit 0), the PR head fails (exit 1). No published stable fiber accepts `react-dom@19.3.0` yet — only `10.0.0-canary.*`. The entry also separates this PR's 2 failures from the 11 that are pre-existing on `main` (P-002, P-007).

## [2026-09-15]

### Added
- **`deliverables/ci/verify_workflows.py`** — a workflow validator that checks the
  thing the repo's existing `lint.py` does not: that each action pin names a
  commit which actually exists. `lint.py` accepts any 40 hex characters, which
  is how `actions/checkout@f548e57c…` sat on `main` through green lint runs while
  every job failed at `Set up job` in two seconds. The new validator makes three
  checks — the file parses as YAML, it exposes `on:` and `jobs:` so GitHub will
  register it (a bare `on:` parses as boolean `True` under YAML 1.1, which trips
  naive checkers), and every `uses:` is a full-length SHA resolved against its
  real repository. It exits non-zero on any failure so it can gate CI, and
  `--check-shas` is opt-in because that pass needs network. Note the `git`
  invocation has to bypass the Fig gitconfig: it rewrites `github.com` to an
  enterprise host that cannot serve public third-party repos. TASK-20260915-003
  records the audit that produced it.

### Added

- **PR #295 (pending)** — `skills/auto-label/` — labels a PR from two signals it
  already carries: the conventional-commit type in its title, and the paths the
  diff touches. The cost of triage is not reading each PR, it is routing it —
  deciding which of the repo's 40 labels applies so a reviewer can filter to
  `skills 🧠` or `security` and ignore the rest. That decision is mechanical for
  the majority of PRs that already follow the repo's commit convention, so it is
  the part worth automating. The skill is additive by construction: `apply.py`
  only calls the add endpoint and never removes a label a human set, a PR that
  matches no rule is left unlabelled rather than guessed at, and the CLI is
  dry-run unless `--apply` is passed. The rule table is data (`labels.json`), so
  behaviour changes without touching `classify.py`. Two deliberate design calls
  are worth naming: the commit *scope* is not a signal (`feat(docs)` with no
  `docs/` path is a feature, not a docs change — the path carries that), and
  precedence is flat, so a PR that is both a skill and documentation gets both
  labels. `deliverables/ci/auto-label.yml` ships the workflow uninstalled because
  the GitHub App lacks the `workflows` scope; its three action pins were
  resolved from the public API and verified to exist, unlike the fabricated SHAs
  already sitting on `main`. TASK-20260915-002 records the work.

- **PR #293** — `docs/fig/` — FIG v4.1 Organization Edition converted from
  jsx-style pseudocode (`FIG.ORG = { ... }` in `.fix/FIG_V4/`) into
  machine-readable JSON config. The specification was readable by people but
  unusable by tooling, so the eight settings it described were transcribed
  verbatim into `docs/fig/config/` — organization identity, MasterFiles policy
  with its four protected paths, the five-layer security flags, the four-role
  permission matrix, the GitHub org rules, the 13 enterprise components, and a
  JSON Schema for audit events with a worked example. Six prose documents sit
  beside them, and `docs/fig/validate_config.py` re-checks the whole
  arrangement — 34 assertions covering parse, fidelity to the source document,
  schema conformance, and the absence of leftover pseudocode. Two gaps are
  recorded rather than papered over: the source does not say whether FIG is a
  code framework or a specification (so no `.jsx` was written), and the GitHub
  rules the document mandates disagree with the repository's current branch
  protection in two places (`require_signed_commits` is off, and
  `require_review_count: 2` is not enforced). TASK-20260915-001 records the
  work. The `.fix/FIG_V4/` original is deliberately left in place as the
  provenance record.

### Changed
- **PR #231** — environment configuration rewritten around per-component
  templates. `.env` was tracked at the root while the codebase reads 148
  distinct variables across its components, so one file could neither document
  them nor stay secret; `.env` is now untracked at every level and each
  component that reads env carries a `.env.example` beside its code —
  `graphql_api/`, `frontend/`, `scripts/`, `deliverables/{pm-backend,
  fastapi-obsidian-backend, agent-security-suite, manus-client}` and
  `deliverables/product-crud/{server,web}`. The root template is regrouped by
  concern with every variable annotated with the file that reads it, and
  `docs/ENVIRONMENT.md` covers the layout, the precedence rules, the
  service-name-vs-localhost distinction between running inside compose and on
  the host, the secrets policy and the CI secret list.
  Two latent defects surfaced and were fixed with it. First, `.gitignore`'s
  `.env.*` pattern matched `.env.example` at every depth, so the new templates
  were written to disk, silently ignored, and would never have been committed —
  negations now track them while `.env` stays ignored. Second,
  `app/core/config.py` declares `JWT_SECRET` and `app/config.py` declares
  `JWT_SECRET_KEY`, both reading the same `.env`: setting only one makes login
  succeed while every subsequent token fails verification. Both are documented
  with that warning, alongside `SENTRY_DSN`, `CACHE_ENABLED` and `CACHE_TTL`,
  which had no template entry at all. `scripts/validate_env_templates.py`
  checks the whole arrangement — 11 templates parse, every declared key
  resolves to a real read in the component it documents, and every variable the
  core app reads is documented. `README.md`'s `docs/` count is corrected for the
  added file (37 → 38), which `deliverables/docs-verify/` caught.

## [2026-09-14]

### Added
- **PR #281** — `deliverables/docs-verify/` — a read-only tool that checks the
  repository's own documentation against the tree. PRs #269/#274/#276 each cited
  `scripts/verify_readme_facts.py` as evidence, but that script lived only in the
  author's workspace, so the evidence could not be re-run by anyone; it is now in
  the repo. Checks README-declared counts (deliverables, docs, workflows — both
  numeral and spelled-out forms), every deliverable being named, backticked paths
  resolving, workflow YAML parse state, the SHA-pin split, the LICENSE holder,
  `package.json`'s `license`, and PROBLEMS.md's structure (unique ids, unique and
  descending date sections). Counts compare against what the README itself
  declares rather than a frozen number, so the checks survive the tree changing
  legitimately and fail only on real drift. 17 tests over synthetic fixture trees.
  On its first run it caught two live drifts from concurrent merges —
  deliverables 25→26 and docs 32→34, both corrected in the same PR. The one
  remaining failure is the known P-001 defect (5 of 11 workflows do not parse).
- **PR #266** — deliverables: added `deliverables/official-docs/`, an official
  documentation registry for the tools and services this project depends on.
  `src/official-docs.json` carries the registry and `src/official_docs.py`
  (Python) plus `src/official-docs.js` / `src/utils.ts` (JS/TS) read it from
  either side of the stack. Every link is verified rather than assumed:
  `scripts/verify_links.py` checks the registry against the live URLs and
  `tests/test_official_docs.py` / `tests/official-docs.test.mjs` cover the
  loaders. The React side (`src/Company.jsx` + `Company.module.css`) renders a
  docs bar and an image gallery from the same registry, so the UI cannot drift
  from the data; `scripts/export_registry.mjs` and `scripts/render_smoke.mjs`
  round out the build-and-check path.
- **PR #265** — deliverables: added `deliverables/fig-best-practices/`, a
  quality gate for projects built on the Fig platform. `BEST-PRACTICES.md` is the
  policy, `SKILL.yaml` wires it up as a skill, and the checker engine runs it
  against a project tree; `ci/quality-gate.yml` is the GitHub Actions entry
  point. Six agent briefs (`agents/developer.md`, `reviewer.md`, `security.md`,
  `designer.md`, `performance.md`, `deployment.md`) state what each role is
  expected to enforce, and `design/design-tokens.json` holds the shared tokens.
  Two fixture projects ship with it — `examples/broken-project/` and
  `examples/clean-project/` — so the gate is exercised against a known-bad and a
  known-good tree rather than only in the happy path. 69 tests.

- **PR #283** — recorded TASK-20260914-001 for today's documentation work
  (README rewrite, `LICENSE` holder, `package.json` licence, `PROBLEMS.md`
  repair, `docs-verify`). The work had merged across twelve PRs but left no
  trace in the repo's own task tracker, which its Definition of Done requires.
  Filed under `inprogress/` rather than `done/` because the out-of-scope items
  — P-001 workflow repair, `.env` key rotation, branch pruning — are still open
  and need an owner call on whether they fold in or split out. Tracker suite
  passes at 20 tests.
### Changed
- **PR #278** — repaired three defects in `PROBLEMS.md`. P-002 claimed 66
  unpinned action refs and its own `[2026-09-11]` re-verify said 23; measured
  today the tree has 60 unpinned of 73 (30 distinct `uses:` values), and neither
  earlier figure reproduces — the entry now carries the per-file breakdown, the
  measurement date, and says plainly that both prior counts are stale rather
  than substituting one unverifiable number for another. `P-009` was shared by
  two unrelated problems (the root `tests/` suite that never collects, and
  `release_drafter.yaml` sitting in `workflows/`), so the latter is now `P-011`
  with a breadcrumb; `docs/releases/v1.2.0.md` cited that ambiguous id. Two
  `## [2026-09-11]` sections also existed on opposite sides of `[2026-09-10]`,
  breaking reverse-chronological order — consolidated into one, with no entry
  changing date. Verified: 12 entry headings and 11 code fences before and
  after, ids `P-001`..`P-011` all present and unique.
- **PR #276** — declared the MIT license in `package.json`. The root
  `package.json` carried no `license` field at all, so npm tooling and GitHub's
  license detection had nothing to read even though `LICENSE` has been MIT from
  the start; added `"license": "MIT"` after `version`. `"private": true` is
  unchanged. Removed the completed item from the README order-of-attack list and
  renumbered the remaining four, and the fact-check script gained an assertion so
  the field cannot drift back: 71 checks, 0 failed. Edit is a single inserted
  line — key order, quoting and trailing-newline style preserved.
- **PR #274** — filled in the `LICENSE` copyright holder. Line 3 read
  `Copyright (c) 2026 [zyntromedia]`, placeholder brackets never removed, so the
  file named no real holder; it now reads `Copyright (c) 2026 Zyntro Media`,
  matching the ZyntroAI organisation display name (the placeholder text was that
  same name, uncleaned). Removed the README bullet that reported the placeholder
  as outstanding, and inverted the fact-check assertion with it —
  `scripts/verify_readme_facts.py` used to assert the placeholder was present,
  it now asserts the holder is filled: 70 checks, 0 failed.
- **PR #269** — rewrote `README.md` so it matches the repository as it stands
  (+119/−767). The previous content was a pasted CI/CD-and-branch-strategy draft
  that described controls, workflows and branches this repo does not have: it named
  `Origin` as the primary integration branch (`main` is the default and the only PR
  target; `Origin` is not in sync and triggers nothing), listed six workflows that do
  not exist (`cd-deploy.yml`, `scheduled-cleanup.yml`, `notify.yml`, `codeql.yml`,
  `container-scan.yml`, `masterfiles-guard.yml`), and asserted protected paths
  (`masterfiles/`, `config/`, `system/`, `settings/`) that are absent from the tree.
  The rewrite states the true CI/CD position — 13 of 73 `uses:` refs SHA-pinned,
  60 still tagged, 5 of 11 workflow files unparseable so they never run — adds a
  deployment-environment table from the live Environments API (`main` has a 15-minute
  wait timer; `Production`/`Preview`/`copilot` have none), and moves every
  not-yet-implemented governance item into an explicit **Target state** section with a
  "Present? No" column. Verified by `scripts/verify_readme_facts.py`: 68 checks, 0
  failed.

- **PR #267** — hardened JWT secret validation and moved users onto a database.
  `app/security.py` now rejects a signing key shorter than 32 characters and
  refuses a set of known placeholder values (`changeme`, `secret`, `jwt-secret`,
  …), so a misconfigured deployment fails loudly instead of signing tokens with
  a guessable key; the local fallback generates a full-strength key written to a
  git-ignored file. Added `app/user_store.py`, a SQLAlchemy-backed user table that
  imports legacy JSON users on first init, keeping the existing
  `{username, hashed_password, allowed_skills}` shape so the API surface and
  per-user skill gating are unchanged. `DATABASE_URL` selects Postgres, otherwise
  SQLite. Verified: 43 tests pass in a clean venv.

### Fixed
- **PR #262** — chore(lint): dropped the unused `import sys` from
  `knowledge/scripts/diff_policy.py`, the only unreferenced import left in the file.
  Supersedes **#253**, which asked for the same cleanup but branched from an older
  59-line snapshot of the file while `main` had moved on to 188 lines — the diff no
  longer applied, so it sat `CONFLICTING / DIRTY` as a draft. `import os`, the other
  name #253 removed, is not imported on `main` at all. Verified: the file compiles
  and an AST pass reports no unused imports beyond `__future__.annotations`.

- **PR #287** — recorded the P-001 workflow repair and shipped it as a verified
  patch. Five files under `.github/workflows/` were not valid YAML so GitHub never
  ran them; the repair is complete and `git apply --check` confirms
  `patches/pr-repair-workflows.patch` applies clean to `main`, after which
  `yaml.safe_load` parses 10/10 files. It cannot be pushed as a PR — the App lacks
  the installation-scoped `workflows` scope (P-003). Two false claims were
  corrected while verifying: `ci.yml` was never broken (PR #230 repaired it before
  P-001 was filed) and the README asserted all eleven files parse when only six do.
  P-001 is marked **FIX PREPARED**, not FIXED — nothing is applied on `main` yet.

- **PR #289** *(opened — pending merge)* — `tests/test_claude_endpoints.py` was chat
  prose wrapped around a fenced code block, so it did not parse
  (`SyntaxError: invalid character '→' (U+2192)`). Because pytest imports every
  file under `tests/`, that single file failed collection for the whole directory
  and blocked every valid test beside it. Extracted the real code, corrected three
  defects in it, and supplied the module it imports but that never existed
  (`app/services/claude_client.py`, an httpx-based Claude client — no new SDK
  dependency). Two pre-existing faults that made `app.services` unimportable were
  fixed alongside: `app/services/__init__.py` imported `UserService`, which
  `users.py` never defined (it defines `UserRepo`), and because a package
  `__init__` runs before any submodule this took down `app.main` too — it now
  resolves lazily (PEP 562); and `app/core/config.py` raised on the repository's
  own `.env` (undeclared keys plus a required `OAUTH_CLIENT_ID`), fixed with
  `extra = "ignore"` and a default. The three test defects: `lines == 'data: {...}'`
  compared a `list` to a `str` (never true), `tool_calls["name"]` indexed a list
  with a string, and the SSE stream terminated with `data: "[DONE]"` (JSON-quoted)
  instead of the bare `data: [DONE]` sentinel clients match on. Verified:
  4/4 tests pass; collection errors across `tests/` fall from 10 to 5, with no new
  ones — every remainder is present on `main` unchanged. Note: `app/.gitignore`'s
  bare `service*` rule would have silently excluded the new client module, so it
  is force-added. **Not** included: `app/db/repositories.py` (`AsyncSession`/`Item`
  undefined) is the other 5 errors and belongs in its own PR.


## [2026-09-13]

### Added
- **PR #245** — docs(knowledge): gave the knowledge notes an index, a manifest and
  front matter. Added `knowledge/README.md` (note table plus a tag table carrying
  per-tag counts and members), `knowledge/manifest.yml`, and
  `knowledge/sync_knowledge_index.py` (dry-run by default) to derive a machine-readable
  index from the notes. YAML front matter added to the six Supabase notes so the index
  and the vault agree on `title`/`description`/`tags`/`supabase_area`/`doc_kind`/`status`.
- **PR #240** — skills: added `ci-workflow-authoring`, a skill for writing workflows
  that run on the first attempt, plus `lint.py` to check them. `lint.py` validates YAML
  parse, required top-level keys, per-job `runs-on`/`steps`, `uses`-or-`run` on every
  step, full-SHA pinning, concatenated documents and hardcoded credentials, exiting
  non-zero so it drops into CI as-is. Pointed at this repository it flagged 9 of the
  10 workflows then on `main` — every one for the same reason, an unresolvable action
  ref in `Set up job`, which is why every PR showed red checks regardless of its diff.
  One subtlety it had to learn: PyYAML resolves a bare `on:` key to boolean `True`
  (YAML 1.1), so a naive `"on" in doc` check reports every valid workflow as missing
  its trigger — its first run flagged all three of its own examples. 16 tests. Three
  corrected example workflows accompany it, each annotating what the draft it came
  from got wrong; they live under `examples/` rather than `.github/workflows/` because
  pushing there needs the `workflows` permission.
- **PR #238** *(opened — pending merge)* — skills: added `pr-triage-automove`, the
  automated form of `organize-misplaced-files`. A root file is relocated only when
  all three hold: it is not canonical (`config.py` allow-list), no tracked `.py`
  imports it as a module (**AST-parsed** — Python 3 resolves `import auth` inside
  `app/api/auth.py` to top-level `auth`, so only the import graph separates a
  sibling from root `auth.py`), and its name appears in no other tracked text file.
  Wraps the move in an import probe: `classify → probe(before) → git mv →
  probe(after) → regression?`, run in a child process so a poisoned import cannot
  kill the run. A FAIL that was already a FAIL is **not** a regression (this repo's
  `app.main` / `main` are deliberately not blocking), UNKNOWN never blocks, and on a
  real regression every `git mv` is reversed with exit 2. Dry-run is the default;
  `--apply` is required to move anything. 37 tests pass; an `--apply` run against a
  copy of this repo moved 112 files as 112 renames with 0 deletions and identical
  import health before/after. Reference workflow in `examples/` carries full-SHA
  pins and is report-only by default.

### Changed
- **PR #237** *(opened — pending merge)* — chore: archived 109 misplaced root files
  to `archive/root-2026-09/` via `git mv` (**no deletions** — the diff is 109
  renames). A file moved only when it was not canonical, no tracked `.py` imported
  it (AST-verified), and its name appeared in no other tracked file. 56 root files
  were kept, several of which look like clutter and are not: `ci.yml`,
  `codeql.yml` and `deployment.yaml` are named by `FILE-MANIFEST.md`,
  `k8s/README.md` and `k8s/kustomization.yaml`; `Plan` by `ROADMAP.md`;
  `context_guard_4060.py` by `app/core/context_guard.md`. Added `pyproject.toml` —
  the Makefile ran `ruff check app tests` and declared black/isort/mypy in
  `requirements-dev.txt`, but there was no config for any of them at the root, so
  lint ran on defaults. Also added two skills, `organize-misplaced-files` and
  `pr-full-lifecycle`.
- **PR #236** — docs: rewrote `README.md` to describe the repository as it stands
  rather than as it was intended. The previous text presented an OAuth2-only service;
  the tree actually holds three FastAPI entrypoints (`main.py`, `app/main.py`,
  `app/core/main.py`), a GraphQL service, a frontend, 20 deliverable suites, skills and
  docs. The replacement adds a quick start that runs, a table of entrypoints naming
  which one `app/Dockerfile` and `vercel.json` actually serve, a split between required
  and optional configuration, the real test command, and a `Known state` section
  recording what is genuinely broken — the tracked `.env` holding live keys, the root
  Node tooling declared but not wired, the root `Dockerfile` being a Node build — with
  counts that can be checked (20 `uses:` SHA-pinned, 61 still on tags).
- **PR #233** — ci: activated the WhatsApp notification workflow. The workflow
  action moved from `templates/workflows/notify-whatsapp.yml` (inert — `templates/`
  is not read by Actions) to `.github/workflows/notify-whatsapp.yml`, with the
  comment header updated to describe the live triggers (push to `main`, plus
  completion of the `Test & Coverage` workflow) and the required secrets.
  `docs/notifications/WHATSAPP.md` now documents the workflow as active instead
  of a template to copy.

### Fixed
- **PR #243** — ci: repaired `auto-compress-manage.yml`, which had failed at
  `Set up job` on all 781 runs. Five action refs pointed at SHAs that do not exist in
  their upstream repositories (confirmed against the commit API, `No commit found for
  SHA`): `calibreapp/image-actions`, `peter-evans/create-pull-request`,
  `stefh/ghaction-CompressFiles`, `actions/checkout` and `actions/upload-artifact`.
  Each was replaced with a verified commit. Four skip conditions were added at the same
  time — `on.paths` globs so commits touching no image or web file skip the workflow
  entirely, and a bot-loop guard so `scan` skips `auto/*` branches and commits carrying
  `[skip ci]` — because adding the guard without fixing the refs would have left the
  workflow failing anyway. Delivered under `deliverables/ci/` (workflow, README and a
  validating script) for application to `.github/workflows/`.
- **PR #237** *(opened — pending merge)* — the FastAPI app entrypoint could not be
  imported. (1) `app/services/__init__.py` did `from .users import UserService`, a
  class that has never existed in that package (`users.py` defines `UserRepo`,
  `get_repo`, `fanout_profile`); because a package `__init__` runs before any
  submodule import, that one wrong name broke every `from app.services.<x> import y`
  and stopped `app.main` — the entrypoint in `app/Dockerfile` and `vercel.json` —
  from importing at all. It now carries no package-level imports, matching
  `app/__init__.py`. (2) `app/core/config.py` used the pydantic v1 `class Config`
  and pydantic v2's default `extra="forbid"`, so the repo's own `.env` (WhatsApp and
  BytePlus keys the app never declares) made `Settings` raise at import; switched to
  `SettingsConfigDict` with `extra="ignore"`. (3) `requirements.txt` was missing ten
  modules that `app/` imports — `pydantic-settings`, `python-jose`, `PyJWT`,
  `python-json-logger`, `redis`, `sqlalchemy`, `alembic`, `requests`, `slowapi`,
  `prometheus-fastapi-instrumentator` — so a fresh install failed at import.
  Verified before/after with the same import probe: `main` and `app.main` go
  FAIL → OK (8 routes). `app/core/main.py` was already broken on `main` and is left
  that way: it imports `auth_router`, `init_db`/`close_db` and
  `items_router`/`users_router` that no longer exist, and repairing it means
  deciding what those APIs should be — recorded in `README.md` rather than guessed at.

## [2026-09-12]

### Added
- **PR #212** — docs: added `docs/MCP-Guide-Complete.md` (MCP-DOC-2026-0912), a
  Thai-language troubleshooting and setup reference for Model Context Protocol
  servers covering the three most common failure modes: Google Cloud ADC
  (`DefaultCredentialsError`, `gcloud auth application-default login`, quota
  project, service-account path, and an explicit warning not to commit
  credentials), missing runtimes (Node.js / Dart / Go install links, per-shell
  PATH setup, the caveat that GUI MCP clients do not read shell profiles, and
  the `.agent/settings.json` → `mcp/servers.json` config shape), and third-party
  API keys (Antimetal / Lovable / Mobbin / Windsor — safe storage order,
  `.env.example` convention, and how to verify a secret never reached git
  history). Also added `scripts/check-mcp-environment.sh`, an automated checker
  for the same three issues with `--gcp` / `--runtimes` / `--keys` flags and a
  CI-suitable exit code; it never prints secret values, only set/not-set. Linked
  from `docs/README.md`.
- **PR #206** — obsidian: connected the `fastapi-obsidian-backend` deliverable to a
  running Obsidian vault via the Local REST API plugin. Adds `app/obsidian/client.py`
  (vault list/read/write/append/patch/delete, active, JsonLogic + simple search, tags,
  commands, open; injectable transport so the whole surface is testable without a vault)
  and `app/routers/obsidian.py` (`/obsidian` endpoints — reads open, writes require a
  valid JWT **and** `OBSIDIAN_ALLOW_WRITE=1`; unconfigured bridge returns 503). Vault-
  relative paths only: `..`, absolute paths and NUL bytes are rejected with 422 before a
  request is built, and every payload crossing the boundary is passed through the
  CWE-1321 sanitizer (`app/cwe1321_bridge.py`) which strips `__proto__` / `prototype` /
  `constructor` at any depth. Config (`OBSIDIAN_API_URL` / `_API_KEY` / `_ALLOW_WRITE` /
  `_VERIFY_TLS`) is off by default. 33 tests passing. Also records the CI enforcement
  gate in the suite README and `manifest.json`.

### Fixed
- **Docs** — corrected the CI/supply-chain documentation so it matches the tree.
  (1) `README.md` still carried a copy-pasted boilerplate block that ended in a
  "CI/CD: ผ่าน / Security: ตรวจสอบแล้ว" status line and a "ต้องการให้ผมช่วย:"
  list — it claimed CI was green, which is false, and pasted a `SECURITY.md`
  draft inline. The block is replaced with a verified
  **CI/CD & supply-chain integrity** section: policy (full-SHA pinning), the
  current state measured against `main`, and the reference SHAs for the actions
  `ci.yml` uses. (2) `SECURITY.md` was a chat-style answer wrapped in prose and
  code fences, and it had picked up a "Supply Chain" section describing a
  `verify-sha` job in `ci.yml` and a pin-history row of "76 refs / all 12
  workflow files / repaired 5 fabricated pins" — none of which is true: there is
  no `verify-sha` job and no `.github/workflows/scripts/verify-shas.py`. It is
  rewritten as a normal policy document (supported versions, private-advisory
  reporting, SLA by severity, scope, coordinated disclosure, severity table) with
  a supply-chain section that states plainly that pinning is policy but **not yet
  enforced**, backed by the same measured counts. All SHAs quoted in both files
  were resolved from the actions' own repositories on 2026-09-12.
- **PR #216** — two defects found by auditing the merged MCP guide against the
  actual tree. (1) `scripts/check-mcp-environment.sh --help` leaked source: the
  handler used a fixed line range, `sed -n '2,22p'`, but the comment header ends
  at line 18, so help output ran into the blank line and `set -uo pipefail` — any
  edit that moves the header would silently change what it printed. It now
  prints the leading comment block itself via `awk`. (2) Two paths in
  `docs/MCP-Guide-Complete.md` did not match the repo: the MCP client example
  lives at `deliverables/agent-security-suite/agent_security_suite/mcp_client.py`,
  and `./mcp/servers.json` does not exist — `.agent/settings.json` points
  `"configPath"` at it, so the doc now says that is where config belongs, with a
  note not to commit it. Adds three assertions to `test_mcp_checker.sh` so
  `--help` cannot regress; 17/17 pass.
- **PR #214** — `scripts/check-mcp-environment.sh`: `check_key()` reported the
  length of the variable *name* rather than the value it held. It printed
  `${#_var}`, which is the character count of the literal string `_var` (4), so
  every key reported "ความยาว 4 ตัวอักษร" no matter how long it actually was —
  a constant that reads like a successful check. Now copies the value into
  `_val` and measures `${#_val}`. Found by the new `scripts/test_mcp_checker.sh`
  added in the same PR: a 15-assertion harness covering syntax, executable bit,
  `--help`, each flag, the unknown-flag exit code, the 0/1 result contract,
  secret redaction, and `.env` tracking (with a fixture repo that tracks a real
  `.env` alongside a safe `.env.example`). The length assertion is computed from
  the fixture rather than hardcoded, and it fails against the unfixed script.
  15/15 pass.

## [2026-09-11]

### Added
- **PR #208** — deliverables: added `deliverables/ai-agent-skills/` — 20 agent
  skills plus an AI Context engine. Each skill ships as
  `skills/<id>/{SKILL.md,schema.yaml}` with its interface, actions and
  least-privilege scopes, catalogued in `registry.yaml` / `registry.json`
  and validated against `ai.context.schema.json`. The engine is
  dependency-free Node: `matcher.js` scores skills by exact target,
  word-bounded keyword and category, and `router.js` turns that ranking
  into a plan that refuses any step whose scopes have not been granted and
  defaults to dry-run for mutating ones (`:write` `:send` `:invoke`
  `:purge` `:authorize`). No secrets are stored anywhere — credentials are
  referenced by name only, and a test scans the registry and schemas for
  common key patterns. 13 tests via `node:test`.
- **PR #202** — notifications: added `scripts/whatsapp_notify.py` (WhatsApp Cloud API
  client — `test_connection`, `send_message`; env-only config, no secrets in code),
  `tests/test_whatsapp_notify.py` (9 tests, HTTP mocked, incl. `code=100/subcode=33`),
  `docs/notifications/WHATSAPP.md` (secrets setup, endpoint shape, error table), and
  `templates/workflows/notify-whatsapp.yml` (SHA-pinned workflow template, kept outside
  `.github/workflows/` because the App lacks `workflows` permission).
- **PR #197** — deliverables: added `deliverables/onspace-platform-integration/` —
  extracted the OnSpaceAI reliability engine out of the standalone app in
  `deliverables/onspace-ai/` and turned it into a reusable AI infrastructure
  service. `OnSpaceAIService` is an async engine with **no FastAPI import**
  (enforced by `tests/test_architecture.py`, which fails if the layering
  regresses); `api.py` is a thin HTTP layer that maps typed exceptions to
  413/503.

  Providers became a config-driven package (`base` + `openai` + `anthropic` +
  `google` + `mock`) replacing the previous hardcoded pair; `factory.build_service()`
  is the single composition root so REST, GraphQL, a worker, and a CLI all get
  the same configured engine; `config.py` uses an `ONSPACE_*` env prefix so
  workers and CLIs need no OAuth env. 58 tests. The original
  `deliverables/onspace-ai/` is untouched at 31 tests and retained as the
  migration source. Ships `README.md`, `MIGRATION.md` (plan steps 1–3 done,
  4–8 pending with the blocker named), and `ADR-001`.
- **PR #193** — docs: added `docs/github-api.md` — a complete GitHub REST v3 +
  GraphQL v4 reference and implementation guide. Covers authentication (PAT,
  GitHub App, installation tokens, a required-scope table), core REST endpoints
  (user, repositories, file contents, issues, pull requests, workflows/Actions)
  with runnable `curl` examples and sample JSON, GraphQL queries/mutations and
  efficient fetching patterns, SDK usage (PyGitHub, `gh` CLI, Octokit), and
  enterprise best practices (rate limits, pagination, error handling, security,
  conditional requests, idempotency). Also added
  `schemas/github-api-schema.json` with example request/response payloads for
  each documented operation.
- **PR #187** — deliverables: added `deliverables/product-crud/` — a full-stack
  Products CRUD reference implementation. Backend is Express + Prisma + Zod in
  five layers (Zod schema → service → controller → routes → mount) with
  pagination, case-insensitive search across `name`/`sku`/`description`, and a
  central error handler returning one shape for `BAD_REQUEST` / `NOT_FOUND` /
  `CONFLICT`. Frontend is Vite + React + TanStack Query, with page, search and
  sort carried in the query key so each page and search term caches separately,
  and `placeholderData: keepPreviousData` so paging dims the table instead of
  flashing a full loading state. 30 tests, no database needed.
  Also ships `docker-compose.yml` (Postgres with a `pg_isready` healthcheck so
  `db:up` can migrate safely), a 30-row idempotent seed script spread across all
  three statuses and deliberately larger than the default page size, and a
  three-stage production `Dockerfile` whose entrypoint applies the Prisma schema
  before starting.

### Fixed
- **PR #198** — `app/__init__.py`: the package no longer imports anything, so
  `import app` works again. It previously built a *second* FastAPI app and ran
  `FastAPIInstrumentor.instrument_app(app)` before the object existed
  (instrumenting on line 37, constructing on line 43), imported the
  never-existing `app.routes`, and pulled in `slowapi` plus six `opentelemetry`
  packages that are absent from the root `requirements.txt`. The result was a
  `ModuleNotFoundError` on any import of the package, including test collection.
  Nothing referenced it — every entrypoint serves `app.main:app`
  (`app/Dockerfile`, `backend/Dockerfile`, `graphql_api/Dockerfile`, `Makefile`),
  and the only `from app import …` statements live in `graphql_api/`, which has
  its own `app` package. Added `tests/test_app_package_init.py` (5 static AST
  checks, no OAuth env or instrumentation packages needed) to prevent the
  regression. Merged 2026-09-12 (squash `b282b9e`).
- **PR #189** — deliverables: patched Dependabot alert #101
  (`GHSA-5xrq-8626-4rwp`, `CVE-2026-47429`, critical) in
  `deliverables/product-crud/server/`. `vitest` 2.1.9 → 4.1.11; going to 4.x
  rather than the minimum patched 3.2.6 also clears the separate moderate
  `@vitest/mocker` path-traversal advisory that 3.2.7 still carried. The suite
  is synchronous, `node`-environment and imports only
  `describe`/`expect`/`it`/`vi`/`beforeEach`, so the major bump needed no test
  changes. Also cleared the two moderate prod findings `npm audit` reported
  separately: `express` requires `qs ~6.15.1` and every release in that range is
  affected, so an `overrides` entry pins `qs` to 6.16.0 — the first patched
  release — rather than forcing an `express` major. `npm audit` now reports 0
  vulnerabilities, prod and dev alike.

### Changed
- **PR #191** — chore: moved the root test runner from `jest` to `vitest`
  (`vitest` + `@vitest/coverage-v8`, with `test` / `test:run` / `test:coverage`
  scripts), and added the `vitest.config.mjs` the switch needs. Without a root
  config `vitest run` walks the whole tree and collects
  `deliverables/cwe1321-protection-suite/tests/sanitize.test.mjs` — a
  `node:test` file — then exits 1 with "No test suite found in file"; the config
  scopes collection to the root project and excludes the self-contained
  deliverable packages. Also added `node_modules/` and `coverage/` to
  `.gitignore`, which the repo root had been missing, and committed the first
  root `package-lock.json`.

### Added — Production Docker image (`deliverables/product-crud/server/`)
- **PR #188** — a three-stage `Dockerfile` (`deps` → `build` → `runtime`) for
  the product-crud API, running `node:22-alpine` as non-root (uid 1001) with
  `tini` as PID 1, since the app relies on SIGTERM for its graceful shutdown,
  and a `HEALTHCHECK` against `/health` using Node's global `fetch`. The module
  has no committed `prisma/migrations/`, so the accompanying
  `docker-entrypoint.sh` inspects the filesystem — `migrate deploy` when
  migrations are present, `db push` otherwise — because a bare
  `migrate deploy` would exit 0 having done nothing and leave the container
  reporting healthy with the tables missing. `SCHEMA_SYNC=auto|deploy|push|none`
  overrides it, and a missing `DATABASE_URL` fails fast. `prisma` moved from
  `devDependencies` to `dependencies` so the CLI survives `--omit=dev`.

### Notes
- **PR #190** was closed unmerged as a duplicate of #191: same `jest` → `vitest`
  change to the root `package.json`, opened a minute earlier, but without the
  `vitest.config.mjs` or the `.gitignore` entries, so merging it alone would have
  shipped a `test:run` script that exits 1 on first use.

## [2026-09-10]

### Added
- **PR #169** — deliverables: added `deliverables/pure-agent-dev/` (Issue #63 reference implementation — provider-agnostic Agent on FastAPI; `ComputeProvider` ABC with mock + BytePlus ECS adapters, planner/executor split, DI-based provider selection via `COMPUTE_PROVIDER`, external JSON Schema contract, Docker + compose, 47 tests). The guide's core rule — the Agent must not depend on the BytePlus SDK — is enforced by `tests/test_architecture.py` walking the real import graph, not by convention. All tests run on the mock provider; no cloud credentials needed.
- **PR #170** — docs: recorded PR #169 in this changelog.
- **PR #175** — tasks: added an `archive/` status to the task tracker (`new.inprogress.done/`) as a terminal folder for work closed without shipping (superseded, abandoned, or duplicate), kept outside the `new -> inprogress -> done` flow. `tools/tasks.py` gains the status plus an `ACTIVE_STATUSES` split, and `archive <id> "<reason>"` moves a task and records the reason in its Completion summary.
- **PR #176** — docs: recorded PR #175 in this changelog.
- **PR #168** — chore(workflows): moved 7 non-workflow files (markdown notes and `.yml.txt`) out of `.github/workflows/` into `archive/workflows-junk/`, leaving the directory holding only real workflows.
- **PR #174** — deliverables: added `deliverables/pm-backend/` — a FastAPI app with provider-neutral billing (Stripe / Chargebee / Paddle adapters behind one interface), CSV reconciliation, and sandbox integration tests (58 passed, 15 skipped).
- **PR #178** — deliverables: added `deliverables/agent-core/` — a runnable, tested FastAPI backend for provider-agnostic agent tasks (async `httpx` client, bounded retry + polling, Supabase task store with RLS, `schema.sql`). Ported from the single-file "Dola Core" draft and renamed Dola → Agent. Fixes that made it actually start: lazy settings (import no longer needs credentials), async I/O instead of blocking `requests`, retry that preserves the original error, bounded polling, and a real persistence layer. 25 offline tests.
- **PR #179** — tasks: added `TASK-20260910-005` recording the five things PR #178 could not prove (placeholder base URL, unverified response field names, unapplied Supabase schema, untested RLS, never-run CI example). Also fixed a tracker bug: `TASK_TEMPLATE.md`'s `status:` comment was copied verbatim by `cmd_new`, breaking three tests that read the template.
- **PR #180** — docs: recorded PR #178 and #179 in this changelog.
- **PR #181** — docs: added `PROBLEMS.md` as the companion to this file, tracking open issues and blockers in the same date sections.
- **PR #182** — tasks: closed `TASK-20260910-005` (→ `done/`) with its Completion summary citing both `CHANGELOG.md` and `PROBLEMS.md` P-004. Also corrected two stale records: `TASK-20260910-004` was renamed to match its id and its validation table filled with measured numbers, and `TASK-20260910-003` gained a re-check showing its fix is still not on remote.
- **PR #183** — docs: recorded PR #180–#182 here, added `PROBLEMS.md` P-007 (new-crystalcastle CI reads a `requirements.txt` that does not exist at the root) and P-008 (the `example-task.md` naming bug), and opened `TASK-20260910-006` to own P-007.
- **PR #184** — docs: recorded PR #183 in this changelog.
- **PR #185** — deliverables: added `deliverables/fastapi-obsidian-backend/` — a FastAPI backend for the Obsidian knowledge workflow with six routers (`skills`, `programs`, `billing`, `tools`, `users`, `security`), opt-in encryption at rest, bundled `data/skills/` markdown, and a pinned `requirements.txt`.
- **Commit `de284dc`** (direct, not a PR) — chore: added a root `package.json` for Node tooling (`vercel`, `eslint`/`prettier`, `jest`, `semantic-release`). The same commit carried ~800 files that had accumulated untracked in the working tree — dashboard `.txt` and `.csv` exports, notebook HTML dumps, stray top-level `.py`/`.yml` fragments, and a `.zip`. Flagged in `README.md` under repository health; it has not been reviewed or pruned.

### Fixed
- **Issue #63 closed** — the `pure-agent-dev` implementation merged to `main` via PR #169 (squash `590b8615`); the issue was closed by the PR's `Closes #63` reference. No `.github/workflows/` files were touched, so the merge was not blocked by the App's `workflows` restriction.

## [2026-09-09]

### Added
- **PR #164** — docs: added `deliverables/ai-gateway-architecture-review/` — systematic AI Gateway architecture review focused on resilience & cost control, plus `deliverables/README.md` index update.
- **PR #165** — deliverables: added `deliverables/onspace-ai/` (FastAPI cost+reliability stack — Redis/memory fail-open cache, circuit breaker, fallback router, token budget + context compiler, Prometheus metrics, k8s manifests; 31 tests), `deliverables/manus-client/` (Manus REST API v2 async client on dot-notation endpoints `task.create`/`task.listMessages`; 10 tests), `deliverables/firecrawl-fastapi/` (FireCrawl + FastAPI production scraper/crawler, firecrawl-py <2.0.0 v1.x surface; 6 tests). All no workflow files, runnable via mock/fail-open.
- **PR #155** — scaffold: added the ZyntroAI merged monorepo scaffold as additive (no-clobber) new files — FastAPI/SQLModel async backend (JWT auth, Alembic, Item CRUD, 6 passing tests), React+Vite+TS frontend, Obsidian↔Algolia knowledge indexer, k8s manifests, 6 typed PR templates, and spec docs. No existing main file modified.
- **PR #160** — docs: rewrote `README.md` to reflect the actual repo structure (OAuth2 PKCE FastAPI core, `graphql_api/`, `skills/`, `deliverables/`, `docs/`, `helm/` + `k8s/`, `tests/`), replacing the stale self-referential comparison doc.
- **PR #158** — docs: added root `RELEASE.md` release guide (semantic-versioning policy, release flow, release-drafter auto-label mapping, verification checklist, rollback guidance).
- **PR #156** — docs: filled `SECURITY.md` with a real security policy (supported versions, private-advisory reporting flow, expected-response SLA by severity, repo security practices); added default `.github/PULL_REQUEST_TEMPLATE.md` pointing typed changes to the 6 specialized templates.
- **PR #150** — docs: added `deliverables/gemini-cli-skills/`: research brief on google-gemini/gemini-cli docs & skills architecture, `AGENTS.md` + `SKILLS.md` overlay index, `@zyntroai` skill overlay templates (github/pull-request, coding/typescript, devops/ci-cd, security/secret-scan), canonical `templates/skill-template.ts`.
- **PR #148** — feat(security): added `deliverables/cwe1321-protection-suite/` — CWE-1321 Prototype Pollution Protection Suite: JS rules (ESLint config, Semgrep, CodeQL query, `sanitize.js` utility) + Python rules (Bandit config, Semgrep, `safe_parser.py` FastAPI/Pydantic-safe loader), `manifest.json`, `SKILL.md`, README, test report, and runnable tests (`sanitize.test.mjs` + `test_safe_parser.py`).
- **PR #147** — docs: added dev/prod `.bicepparam` examples (F1 / P1v2) under `deliverables/azure-cli-2026/examples/bicepparam/`.
- **PR #146** — docs: added full Bicep/IaC appendix to `deliverables/azure-cli-2026/azure-cli-2026.md` (`az bicep` build/decompile/lint/publish, standard file structure, sample templates, CLI deploy + what-if + security, GitHub Actions workflow commands); new `docs/README.md` + `deliverables/README.md` indexes; new `docs/github-actions/workflow-commands-reference.md`; new example workflow `deliverables/azure-cli-2026/examples/azure-bicep-deploy.yml`.
- **PR #145** — docs: added Azure CLI 2026 flashcards & one-page cheat sheet to `deliverables/azure-cli-2026/azure-cli-2026.md`.
- **PR #142** — extended `deliverables/notebooklm-access-suite/` to full sub-skill set: validate/guide/link_security/provenance/verify/knowledge (read-only, evidence-based). Suite now 22 tests.
- **PR #140** — added `deliverables/notebooklm-access-suite/`: NotebookLM access-artifact suite core P0 (resolver/access/artifact), evidence-based read-only access classification. 12 tests.
- **PR #138** — added `deliverables/agent-skill-template/`: standard agent-skill template (JSON+YAML), progressive-disclosure loader (`load_skill`/`resolve_layers`/`verify_gates`/`prepare_skill`), NotebookLM filled example. 11 tests.
- **PR #136** — added `deliverables/notebooklm-link-share/`: NotebookLM link-share skill (`notebooklm_link_share`), normalize/validate/share-templates, pure stdlib, SKILL.yaml. 9 tests.
- **PR #134** — added `runpod_client.py` to `deliverables/agent-security-suite/`: RunPod client (lazy import), ACTION_SCHEMA validation, audit hook, `connect_runpod()`. Suite now 28 tests.
- **PR #132** — added `ci_ops` module to `deliverables/agent-security-suite/`: permission-aware checks (contents:write ≠ workflows:write), SHA-pin scan, CI root-cause fingerprint. Suite now 21 tests.
- **PRs #125–#130** — Dependabot: docker base bumps (alpine 3.24, node 26, python 3.14), npm (vercel), pip (production-deps), npm dev-deps.
- **PR #122** — extended `deliverables/agent-security-suite/`: LangGraph time-travel recovery (`recovery.py`) + MCP client (`mcp_client.py`), lazy-imported (core runs without them). Now 11 tests.
- **PR #120** — `deliverables/agent-security-suite/`: runnable core (ISO-27001-style SQLite audit log with SHA-256 payload hash, JSON-schema validation, stdlib-only Slack alert). 7 tests.
- **PR #118** — `skills/research/`: multi-source knowledge synthesis (ResearchSkill.run) built on fetching — dedupe, cross-validation to 0.0–1.0 confidence, contradiction flags, provenance graph + checksum. 7 tests.
- **PR #116** — `skills/fetching/` extended with async GraphQL (`clients/graphql.py`, TTL cache) and WebSocket (`clients/websocket.py`, wss/ws, lazy `websockets`) clients; `ssrf.check_ws()`. Now 17 tests.
- **PR #114** — `skills/fetching/`: SSRF-safe async HTTP fetch skill (httpx) with retry + TTL cache + provenance; SSRF guard blocks private/local/metadata hosts; GitHub source. 9 tests.
- **PR #112** — Reference deliverables under `deliverables/`: GitHub DevOps Toolkit (PR templates, SHA-pinned gatekeeper workflows, externalized branch-protection config, Terraform module) + AI Agents Decision Pack (comparison matrix, Notion/Figma/Miro assets). Docs/config only.

## [2026-09-08] — Skill-native architecture, secrets cleanup, and GraphQL API

### Added — GraphQL API (`graphql_api/`, self-contained subproject)
- **PR #107** — Integrated a self-contained FastAPI + Strawberry GraphQL service under `graphql_api/` (JWT auth, `me`/`users` cursor-paginated queries, `login`/`create_user` mutations, subscription scaffold, async SQLAlchemy, `/health`, Dockerfile + compose).
- **PR #109** — DB-backed resolvers + Alembic migrations: async CRUD (`crud.py`, bcrypt hash/verify), initial migration creating the `users` table, resolvers reading/writing the database.
- **PR #110** — Redis pub/sub subscriptions (real `user_created` event + publish on `create_user`), `@cache_resolver` decorator utility, standardized GraphQL errors (`PermissionDenied`/`AuthenticationRequired`/`ResourceNotFound` with `code`/`status` extensions).

### Added — Central credential management + workflow guardian
- **PR #104** — `app/core/credential_broker.py` (thin async broker client, metadata-only, tolerates an unconfigured broker), `app/skills/credential_management` + `workflow_guardian` client wrappers, `credentials/registry.yaml` (references only), `requirements/skills.txt`.

### Changed — Security & config fixes
- **PR #105** — Untracked `.env` (was committed with real secrets despite `.gitignore`); added safe `.env.example` (placeholder/vault references) + `vault/` policy and app-role.
- **PR #106** — Fixed `app/config.py` (used `BaseSettings` without importing it) and `tests/conftest.py` (used `AsyncGenerator`/`app`/`get_current_user` without importing them).

### Notes
- Earlier `CHANGELOG.md` content describing a "Claude REST API ecosystem" described files not present in this repository; it has been replaced with this accurate record.
- CI on this repo is red at the "Set up job" step from the org's SHA-pin policy: a job refuses to start when a referenced action is not pinned to a full commit SHA. Measured on **2026-09-10**, `main`'s workflows still mix full SHAs with mutable tags — `actions/checkout@v4` (17 refs), `actions/upload-artifact@v4` (6), `actions/setup-python@v5` (7), `subosito/flutter-action@v2` (5), `somaz94/compress-decompress@v1` (5), `gitleaks/gitleaks-action@v2`, and others.
- The SHA-pin fix requires writing `.github/workflows/`, which the Fig GitHub App is not permitted to do (pushes are rejected with `refusing to allow a GitHub App to create or update workflow ... without workflows permission`). It must therefore be applied by a maintainer, or with elevated App permissions. This is why feature PRs on this repo show red checks even when their own tests pass.
