id: auto-rerun-fail-jobs
name: Failure-Aware CI Recovery Engine
version: 2.0.0
type: devops/ci/automation
description: >
  Intelligent CI recovery: Detect → Fingerprint → Classify → Decide → Rerun ONLY failed jobs → Observe → Report.
  Never retry permanent failures: code, test, permission, security. Save cost & accelerate feedback.

core_flow:
  - Workflow Failed → Collect Jobs/Logs → Fingerprint
  - Classify: Transient / Infra / Dependency / Test / Code / Permission / Security
  - Decide: Policy + Budget + Backoff + Permission Check
  - Execute: RERUN ONLY FAILED JOB (not full workflow)
  - Observe → Track → Log → History
  - Recover → Debug/Patch if non-retryable
  - Report → PR Comment + Project Status Sync

policy:
  max_attempts: 3
  auto_retry:
    transient: true
    infrastructure: true
    rate_limit: true
    dependency: false
    test: false
    code: false
    permission: false
    security: false
  require_approval:
    production_deploy: true
    destructive_job: true
  audit: true
  comments: true
  status_sync: true

permissions_required:
  actions: [read, write]       # ✅ For rerunning jobs
  contents: [read]
permissions_not_required:
  workflows: [write]           # ❌ Rerun ≠ edit workflow

retry:
  strategy: exponential
  initial_sec: 30
  max_sec: 300
  formula: delay = min(initial × 2^attempt, max_sec)
  stop_conditions:
    - success
    - non_retryable
    - budget_exceeded
    - permission_denied
    - security_failure

integration:
  upstream: [github-actions]
  downstream: [credential-management, debug-error, project-status-auto-update, pull-request-comment]
