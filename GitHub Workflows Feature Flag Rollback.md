**Searching for GitHub Actions docs**  
I’m looking into GitHub Actions documentation, focusing on workflow syntax and secrets, to gather relevant information and provide adapted code with proper citations.
Below is a GitHub Actions workflow that enables a feature, validates it, simulates a failure, disables the flag, and confirms the legacy path still works.

```yaml
# .github/workflows/feature-flag-rollback.yml
name: Feature Flag Rollback Test

on:
  workflow_dispatch:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  rollback-test:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    env:
      FEATURE_FLAG: newCheckout
      APP_URL: https://app.example.com

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Make scripts executable
        run: chmod +x ./scripts/*.sh

      - name: Enable feature
        env:
          FLAG_API_TOKEN: ${{ secrets.FLAG_API_TOKEN }}
        run: |
          ./scripts/set-flag.sh "$FEATURE_FLAG" true

      - name: Test new feature
        run: |
          curl --fail --retry 3 "$APP_URL/health"
          ./scripts/test-checkout.sh --expected-version=new

      - name: Simulate failure
        run: ./scripts/inject-failure.sh

      # always() ensures rollback is attempted even when an earlier step fails.
      - name: Disable feature flag
        if: ${{ always() }}
        env:
          FLAG_API_TOKEN: ${{ secrets.FLAG_API_TOKEN }}
        run: |
          ./scripts/set-flag.sh "$FEATURE_FLAG" false

      - name: Validate stable path after rollback
        if: ${{ always() }}
        run: |
          curl --fail --retry 3 "$APP_URL/health"
          ./scripts/test-login.sh
          ./scripts/test-checkout.sh --expected-version=legacy
          ./scripts/test-api.sh
```

Store `FLAG_API_TOKEN` under **Repository Settings → Secrets and variables → Actions**. GitHub requires secrets to be explicitly passed into the workflow, such as through `env`, and recommends granting credentials the minimum permissions necessary. [1](https://docs.github.com/en/actions/concepts/security/secrets)[2](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)

For production, make the rollback step idempotent so disabling an already-disabled flag still succeeds. Also consider placing production credentials in a protected GitHub Environment with required reviewers. [1](https://docs.github.com/en/actions/concepts/security/secrets)

Here’s an updated workflow that captures failures, always attempts rollback, validates the legacy path, and reports the correct final status.

```yaml
# .github/workflows/feature-flag-rollback.yml
name: Feature Flag Rollback Test

on:
  workflow_dispatch:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  rollback-test:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    env:
      FEATURE_FLAG: newCheckout
      APP_URL: https://app.example.com

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Make scripts executable
        run: chmod +x ./scripts/*.sh

      - name: Enable feature
        id: enable_feature
        continue-on-error: true
        env:
          FLAG_API_TOKEN: ${{ secrets.FLAG_API_TOKEN }}
        run: ./scripts/set-flag.sh "$FEATURE_FLAG" true

      - name: Test new feature
        id: feature_tests
        if: steps.enable_feature.outcome == 'success'
        continue-on-error: true
        run: |
          curl --fail --retry 3 "$APP_URL/health"
          ./scripts/test-checkout.sh --expected-version=new

      - name: Simulate failure
        id: failure_injection
        if: steps.feature_tests.outcome == 'success'
        continue-on-error: true
        run: ./scripts/inject-failure.sh

      - name: Disable feature flag
        id: rollback
        if: always()
        continue-on-error: true
        env:
          FLAG_API_TOKEN: ${{ secrets.FLAG_API_TOKEN }}
        run: ./scripts/set-flag.sh "$FEATURE_FLAG" false

      - name: Validate stable path
        id: rollback_tests
        if: always()
        continue-on-error: true
        run: |
          curl --fail --retry 3 "$APP_URL/health"
          ./scripts/test-login.sh
          ./scripts/test-checkout.sh --expected-version=legacy
          ./scripts/test-api.sh

      - name: Publish test summary
        if: always()
        env:
          ENABLE_RESULT: ${{ steps.enable_feature.outcome }}
          FEATURE_TEST_RESULT: ${{ steps.feature_tests.outcome }}
          INJECTION_RESULT: ${{ steps.failure_injection.outcome }}
          ROLLBACK_RESULT: ${{ steps.rollback.outcome }}
          ROLLBACK_TEST_RESULT: ${{ steps.rollback_tests.outcome }}
        run: |
          {
            echo "## Feature Flag Rollback Results"
            echo "| Step | Result |"
            echo "|---|---|"
            echo "| Enable feature | $ENABLE_RESULT |"
            echo "| Feature tests | $FEATURE_TEST_RESULT |"
            echo "| Failure injection | $INJECTION_RESULT |"
            echo "| Disable feature | $ROLLBACK_RESULT |"
            echo "| Rollback validation | $ROLLBACK_TEST_RESULT |"
          } >> "$GITHUB_STEP_SUMMARY"

      - name: Set final workflow status
        if: always()
        env:
          ENABLE_RESULT: ${{ steps.enable_feature.outcome }}
          FEATURE_TEST_RESULT: ${{ steps.feature_tests.outcome }}
          INJECTION_RESULT: ${{ steps.failure_injection.outcome }}
          ROLLBACK_RESULT: ${{ steps.rollback.outcome }}
          ROLLBACK_TEST_RESULT: ${{ steps.rollback_tests.outcome }}
        run: |
          failed=false

          check_result() {
            local name="$1"
            local result="$2"

            if [ "$result" != "success" ]; then
              echo "::error::$name returned: $result"
              failed=true
            fi
          }

          check_result "Enable feature" "$ENABLE_RESULT"
          check_result "Feature tests" "$FEATURE_TEST_RESULT"
          check_result "Failure injection" "$INJECTION_RESULT"
          check_result "Disable feature" "$ROLLBACK_RESULT"
          check_result "Rollback validation" "$ROLLBACK_TEST_RESULT"

          if [ "$failed" = true ]; then
            echo "Rollback test workflow failed."
            exit 1
          fi

          echo "Rollback completed and the stable path was validated."
```

**Key improvements**
- `continue-on-error` prevents failed tests from blocking rollback.
- `if: always()` guarantees rollback and validation are attempted.
- The final step restores the correct failed workflow status.
- `$GITHUB_STEP_SUMMARY` provides a readable result table in GitHub Actions.
**Considering GitHub workflow updates**  
Exploring how to handle test failures, rollback, and status capture in a GitHub Actions workflow, ensuring proper failure reporting and validation while using `continue-on-error` and outcome context.


**Looking into GitHub docs**  
I’m exploring GitHub’s official documentation to understand the current behavior and any relevant details about modifying code, especially regarding the GITHUB_STEP_SUMMARY feature.
This version captures each step’s stdout/stderr with `tee`, preserves exit codes using `pipefail`, and embeds the latest log lines in collapsible summary sections. GitHub renders Markdown appended to `$GITHUB_STEP_SUMMARY`. [1](https://github.blog/news-insights/product-news/supercharging-github-actions-with-job-summaries/)[2](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands)

```yaml
name: Feature Flag Rollback Test

on:
  workflow_dispatch:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  rollback-test:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    env:
      FEATURE_FLAG: newCheckout
      APP_URL: https://app.example.com
      LOG_DIR: ${{ runner.temp }}/rollback-logs

    steps:
      - uses: actions/checkout@v4

      - name: Prepare
        run: |
          mkdir -p "$LOG_DIR"
          chmod +x ./scripts/*.sh

      - name: Enable feature
        id: enable_feature
        continue-on-error: true
        env:
          FLAG_API_TOKEN: ${{ secrets.FLAG_API_TOKEN }}
        shell: bash
        run: |
          set -o pipefail
          ./scripts/set-flag.sh "$FEATURE_FLAG" true \
            2>&1 | tee "$LOG_DIR/enable-feature.log"

      - name: Test new feature
        id: feature_tests
        if: steps.enable_feature.outcome == 'success'
        continue-on-error: true
        shell: bash
        run: |
          set -o pipefail
          {
            curl --fail --show-error --retry 3 "$APP_URL/health"
            ./scripts/test-checkout.sh --expected-version=new
          } 2>&1 | tee "$LOG_DIR/feature-tests.log"

      - name: Simulate failure
        id: failure_injection
        if: steps.feature_tests.outcome == 'success'
        continue-on-error: true
        shell: bash
        run: |
          set -o pipefail
          ./scripts/inject-failure.sh \
            2>&1 | tee "$LOG_DIR/failure-injection.log"

      - name: Disable feature flag
        id: rollback
        if: always()
        continue-on-error: true
        env:
          FLAG_API_TOKEN: ${{ secrets.FLAG_API_TOKEN }}
        shell: bash
        run: |
          set -o pipefail
          ./scripts/set-flag.sh "$FEATURE_FLAG" false \
            2>&1 | tee "$LOG_DIR/rollback.log"

      - name: Validate stable path
        id: rollback_tests
        if: always()
        continue-on-error: true
        shell: bash
        run: |
          set -o pipefail
          {
            curl --fail --show-error --retry 3 "$APP_URL/health"
            ./scripts/test-login.sh
            ./scripts/test-checkout.sh --expected-version=legacy
            ./scripts/test-api.sh
          } 2>&1 | tee "$LOG_DIR/rollback-tests.log"

      - name: Publish results and logs
        if: always()
        env:
          ENABLE_RESULT: ${{ steps.enable_feature.outcome }}
          FEATURE_TEST_RESULT: ${{ steps.feature_tests.outcome }}
          INJECTION_RESULT: ${{ steps.failure_injection.outcome }}
          ROLLBACK_RESULT: ${{ steps.rollback.outcome }}
          ROLLBACK_TEST_RESULT: ${{ steps.rollback_tests.outcome }}
        shell: bash
        run: |
          {
            echo "## Feature Flag Rollback Results"
            echo
            echo "| Step | Result |"
            echo "|---|---|"
            echo "| Enable feature | $ENABLE_RESULT |"
            echo "| Feature tests | $FEATURE_TEST_RESULT |"
            echo "| Failure injection | $INJECTION_RESULT |"
            echo "| Disable feature | $ROLLBACK_RESULT |"
            echo "| Rollback validation | $ROLLBACK_TEST_RESULT |"
            echo

            for log in "$LOG_DIR"/*.log; do
              [ -f "$log" ] || continue

              echo "<details>"
              echo "<summary>$(basename "$log")</summary>"
              echo
              echo '```text'
              tail -n 200 "$log"
              echo '```'
              echo "</details>"
              echo
            done
          } >> "$GITHUB_STEP_SUMMARY"

      - name: Set final workflow status
        if: always()
        env:
          ENABLE_RESULT: ${{ steps.enable_feature.outcome }}
          FEATURE_TEST_RESULT: ${{ steps.feature_tests.outcome }}
          INJECTION_RESULT: ${{ steps.failure_injection.outcome }}
          ROLLBACK_RESULT: ${{ steps.rollback.outcome }}
          ROLLBACK_TEST_RESULT: ${{ steps.rollback_tests.outcome }}
        shell: bash
        run: |
          failed=false

          check_result() {
            if [ "$2" != "success" ]; then
              echo "::error::$1 returned: $2"
              failed=true
            fi
          }

          check_result "Enable feature" "$ENABLE_RESULT"
          check_result "Feature tests" "$FEATURE_TEST_RESULT"
          check_result "Failure injection" "$INJECTION_RESULT"
          check_result "Disable feature" "$ROLLBACK_RESULT"
          check_result "Rollback validation" "$ROLLBACK_TEST_RESULT"

          [ "$failed" = false ] || exit 1
```

`tail -n 200` prevents unusually large summaries. Ensure scripts never print tokens or other sensitive values into captured output.
**Revising workflow for logs**  
I’m considering a revised workflow that ensures logs are captured using `tee` and `PIPESTATUS`. Each step will redirect output with `2>&1 | tee file`, and the exit status will be controlled by `exit ${PIPESTATUS[0]}`. I'll wrap the function and ensure that multiple commands under `set -o pipefail` and braces are piped to `tee`, with the status working as expected. I'll also create a `LOG_DIR` in `runner.temp` to persist logs, ensuring each test step is logged. To sanitize, I’ll append summaries in code fences and use `sed` to limit output to 200 lines, while being cautious not to print secrets.

Add a reusable Bash retry helper, then use it only for idempotent test commands. Each attempt is appended to the existing log files and therefore appears in the workflow summary.

```yaml
env:
  FEATURE_FLAG: newCheckout
  APP_URL: https://app.example.com
  LOG_DIR: ${{ runner.temp }}/rollback-logs
  TEST_MAX_ATTEMPTS: 3
  TEST_RETRY_DELAY: 10
```

Replace the two test steps with:

```yaml
- name: Test new feature
  id: feature_tests
  if: steps.enable_feature.outcome == 'success'
  continue-on-error: true
  shell: bash
  run: |
    set -o pipefail
    LOG_FILE="$LOG_DIR/feature-tests.log"

    retry() {
      local description="$1"
      shift
      local attempt=1

      while [ "$attempt" -le "$TEST_MAX_ATTEMPTS" ]; do
        echo "[$description] Attempt $attempt/$TEST_MAX_ATTEMPTS" \
          | tee -a "$LOG_FILE"

        "$@" 2>&1 | tee -a "$LOG_FILE"
        status=${PIPESTATUS[0]}

        if [ "$status" -eq 0 ]; then
          echo "[$description] Passed" | tee -a "$LOG_FILE"
          return 0
        fi

        if [ "$attempt" -lt "$TEST_MAX_ATTEMPTS" ]; then
          echo "[$description] Failed. Retrying in ${TEST_RETRY_DELAY}s..." \
            | tee -a "$LOG_FILE"
          sleep "$TEST_RETRY_DELAY"
        fi

        attempt=$((attempt + 1))
      done

      echo "[$description] Failed after $TEST_MAX_ATTEMPTS attempts" \
        | tee -a "$LOG_FILE"
      return 1
    }

    retry "Health check" \
      curl --fail --show-error "$APP_URL/health"

    retry "New checkout test" \
      ./scripts/test-checkout.sh --expected-version=new
```

```yaml
- name: Validate stable path
  id: rollback_tests
  if: always()
  continue-on-error: true
  shell: bash
  run: |
    set -o pipefail
    LOG_FILE="$LOG_DIR/rollback-tests.log"
    failed=false

    retry() {
      local description="$1"
      shift
      local attempt=1

      while [ "$attempt" -le "$TEST_MAX_ATTEMPTS" ]; do
        echo "[$description] Attempt $attempt/$TEST_MAX_ATTEMPTS" \
          | tee -a "$LOG_FILE"

        "$@" 2>&1 | tee -a "$LOG_FILE"
        status=${PIPESTATUS[0]}

        if [ "$status" -eq 0 ]; then
          echo "[$description] Passed" | tee -a "$LOG_FILE"
          return 0
        fi

        if [ "$attempt" -lt "$TEST_MAX_ATTEMPTS" ]; then
          echo "[$description] Failed. Retrying in ${TEST_RETRY_DELAY}s..." \
            | tee -a "$LOG_FILE"
          sleep "$TEST_RETRY_DELAY"
        fi

        attempt=$((attempt + 1))
      done

      echo "[$description] Failed after $TEST_MAX_ATTEMPTS attempts" \
        | tee -a "$LOG_FILE"
      return 1
    }

    retry "Health check" \
      curl --fail --show-error "$APP_URL/health" || failed=true

    retry "Login test" \
      ./scripts/test-login.sh || failed=true

    retry "Legacy checkout test" \
      ./scripts/test-checkout.sh --expected-version=legacy || failed=true

    retry "API test" \
      ./scripts/test-api.sh || failed=true

    [ "$failed" = false ]
```

The rollback validation runs every test even if one exhausts its retries, but the step still fails at the end if any test never passes. Avoid retrying feature-flag mutations or failure injection unless those operations are explicitly idempotent.
**Explaining retry function in bash**  
The retry function in bash will execute a command multiple times with a delay between attempts. It captures logs and ensures the command exits based on the final return status.

Add retries around both enable and disable operations, with exponential backoff and post-change verification. This assumes `set-flag.sh` is idempotent and `get-flag.sh` returns `true` or `false`.

```yaml
env:
  FLAG_MAX_ATTEMPTS: 4
  FLAG_RETRY_DELAY: 5
```

Replace the toggle steps with:

```yaml
- name: Enable feature
  id: enable_feature
  continue-on-error: true
  env:
    FLAG_API_TOKEN: ${{ secrets.FLAG_API_TOKEN }}
  shell: bash
  run: |
    set -o pipefail
    LOG_FILE="$LOG_DIR/enable-feature.log"

    change_flag_with_retry() {
      local desired_state="$1"
      local attempt=1
      local delay="$FLAG_RETRY_DELAY"

      while [ "$attempt" -le "$FLAG_MAX_ATTEMPTS" ]; do
        echo "[Feature flag] Setting $FEATURE_FLAG=$desired_state, attempt $attempt/$FLAG_MAX_ATTEMPTS" \
          | tee -a "$LOG_FILE"

        ./scripts/set-flag.sh "$FEATURE_FLAG" "$desired_state" \
          2>&1 | tee -a "$LOG_FILE"
        set_status=${PIPESTATUS[0]}

        if [ "$set_status" -eq 0 ]; then
          actual_state="$(
            ./scripts/get-flag.sh "$FEATURE_FLAG" 2>>"$LOG_FILE"
          )"

          if [ "$actual_state" = "$desired_state" ]; then
            echo "[Feature flag] Verified state: $actual_state" \
              | tee -a "$LOG_FILE"
            return 0
          fi

          echo "[Feature flag] Verification returned: $actual_state" \
            | tee -a "$LOG_FILE"
        else
          echo "[Feature flag] Update failed with exit code $set_status" \
            | tee -a "$LOG_FILE"
        fi

        if [ "$attempt" -lt "$FLAG_MAX_ATTEMPTS" ]; then
          echo "[Feature flag] Retrying in ${delay}s" | tee -a "$LOG_FILE"
          sleep "$delay"
          delay=$((delay * 2))
        fi

        attempt=$((attempt + 1))
      done

      echo "::error::Unable to enable $FEATURE_FLAG"
      return 1
    }

    change_flag_with_retry true
```

```yaml
- name: Disable feature flag
  id: rollback
  if: always()
  continue-on-error: true
  env:
    FLAG_API_TOKEN: ${{ secrets.FLAG_API_TOKEN }}
  shell: bash
  run: |
    set -o pipefail
    LOG_FILE="$LOG_DIR/rollback.log"

    change_flag_with_retry() {
      local desired_state="$1"
      local attempt=1
      local delay="$FLAG_RETRY_DELAY"

      while [ "$attempt" -le "$FLAG_MAX_ATTEMPTS" ]; do
        echo "[Feature flag] Setting $FEATURE_FLAG=$desired_state, attempt $attempt/$FLAG_MAX_ATTEMPTS" \
          | tee -a "$LOG_FILE"

        ./scripts/set-flag.sh "$FEATURE_FLAG" "$desired_state" \
          2>&1 | tee -a "$LOG_FILE"
        set_status=${PIPESTATUS[0]}

        if [ "$set_status" -eq 0 ]; then
          actual_state="$(
            ./scripts/get-flag.sh "$FEATURE_FLAG" 2>>"$LOG_FILE"
          )"

          if [ "$actual_state" = "$desired_state" ]; then
            echo "[Feature flag] Verified state: $actual_state" \
              | tee -a "$LOG_FILE"
            return 0
          fi
        fi

        if [ "$attempt" -lt "$FLAG_MAX_ATTEMPTS" ]; then
          echo "[Feature flag] Retrying in ${delay}s" | tee -a "$LOG_FILE"
          sleep "$delay"
          delay=$((delay * 2))
        fi

        attempt=$((attempt + 1))
      done

      echo "::error::Unable to disable $FEATURE_FLAG"
      return 1
    }

    change_flag_with_retry false
```

The logged attempts will automatically appear in the existing collapsible summary sections. Most importantly, rollback is considered successful only after the disabled state is verified.
**Considering modification steps**  
Looking into how to modify snippets, ensuring no web access is needed. I'll focus on providing steps for retries, verification, and idempotent state setting with logs.

Assuming you mean **feature-flag state snapshots**, capture the original state before testing and restore that exact state afterward.

```yaml
- name: Snapshot original flag state
  id: flag_snapshot
  env:
    FLAG_API_TOKEN: ${{ secrets.FLAG_API_TOKEN }}
  shell: bash
  run: |
    state="$(./scripts/get-flag.sh "$FEATURE_FLAG")"
    echo "original_state=$state" >> "$GITHUB_OUTPUT"
    echo "$state" > "$LOG_DIR/original-flag-state.log"
    echo "Original state: $state"
```

Then restore the snapshot instead of always setting the flag to `false`:

```yaml
- name: Restore feature flag snapshot
  id: rollback
  if: always()
  continue-on-error: true
  env:
    FLAG_API_TOKEN: ${{ secrets.FLAG_API_TOKEN }}
    ORIGINAL_STATE: ${{ steps.flag_snapshot.outputs.original_state }}
  shell: bash
  run: |
    set -o pipefail
    LOG_FILE="$LOG_DIR/rollback.log"
    delay="$FLAG_RETRY_DELAY"

    for attempt in $(seq 1 "$FLAG_MAX_ATTEMPTS"); do
      echo "Restoring $FEATURE_FLAG=$ORIGINAL_STATE, attempt $attempt" \
        | tee -a "$LOG_FILE"

      ./scripts/set-flag.sh "$FEATURE_FLAG" "$ORIGINAL_STATE" \
        2>&1 | tee -a "$LOG_FILE"

      actual_state="$(./scripts/get-flag.sh "$FEATURE_FLAG")"

      if [ "$actual_state" = "$ORIGINAL_STATE" ]; then
        echo "Snapshot restored and verified: $actual_state" \
          | tee -a "$LOG_FILE"
        exit 0
      fi

      sleep "$delay"
      delay=$((delay * 2))
    done

    echo "::error::Failed to restore feature flag snapshot"
    exit 1
```

This prevents the workflow from incorrectly disabling a flag that was already enabled before the test.
**Considering feature flag snapshots**  
It seems like you're asking about capturing the state of a feature flag before toggling it, possibly for testing or restoring the exact state later. I'll assume you're referring to feature flag state snapshots in a workflow.

กำลังค้นหา...
Add a shared `curl` wrapper for transient API failures. Curl retries selected HTTP failures, uses backoff by default, and respects `Retry-After` when provided. [1](https://android.googlesource.com/platform/external/curl/+/refs/heads/main/docs/cmdline-opts/retry.md)

```yaml
env:
  API_RETRIES: 4
  API_CONNECT_TIMEOUT: 5
  API_MAX_TIME: 30
  API_RETRY_MAX_TIME: 120
```

Use this helper in API-related steps:

```bash
api_call() {
  curl \
    --fail-with-body \
    --show-error \
    --silent \
    --connect-timeout "$API_CONNECT_TIMEOUT" \
    --max-time "$API_MAX_TIME" \
    --retry "$API_RETRIES" \
    --retry-max-time "$API_RETRY_MAX_TIME" \
    --retry-connrefused \
    "$@"
}
```

Example health check:

```bash
api_call "$APP_URL/health" 2>&1 | tee -a "$LOG_FILE"
status=${PIPESTATUS[0]}
[ "$status" -eq 0 ]
```

Example feature-toggle update:

```bash
api_call \
  --request PATCH \
  --header "Authorization: Bearer $FLAG_API_TOKEN" \
  --header "Content-Type: application/json" \
  --data "{\"enabled\":$desired_state}" \
  "$FLAG_API_URL/flags/$FEATURE_FLAG" \
  2>&1 | tee -a "$LOG_FILE"

status=${PIPESTATUS[0]}
[ "$status" -eq 0 ]
```

Avoid `--retry-all-errors` for state-changing requests unless the API supports an idempotency key. For example:

```bash
--header "Idempotency-Key: $GITHUB_RUN_ID-$FEATURE_FLAG-$desired_state"
```

Keep the existing state verification after each toggle update, since a successful HTTP response does not by itself confirm that the desired flag state is active.