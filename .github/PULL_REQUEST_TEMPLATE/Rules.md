I need help setting up the rules for closing and moving files

Here’s a practical, opinionated rule set you can drop into your workflow for:

- **When to close PRs**
- **Which files to move where (and when)**  

You can tune the numbers, but this is a solid default for most teams.[1][2][3][4][5]

***

## 1. Rules for closing PRs

Use a **two-stage** policy: **stale → close**. This is what most mature repos do.[1][2][3][4][5]

### 1.1. Inactivity-based close (standard “stale” policy)

**Goal:** Close PRs that are abandoned or no longer relevant.

**Recommended defaults:**

- Mark PR as **stale** after:
  - **60 days** of no activity (no commits, no comments, no reviews).[2][6][7]
- Close stale PR after:
  - **7 days** more of inactivity.[2][4][8][9]

**Exemptions (do NOT auto-close if PR has any of these labels):**

- `work-in-progress` or `WIP`  
- `blocked` or `waiting-on-…`  
- `do-not-close` / `keep-open`  
- `release-blocker` / `critical` (if you use such labels)  

**Messages:**

- Stale message (when marking stale):  
  > This PR has been inactive for 60 days. If it is still relevant, please leave a comment or update the branch. Otherwise, it will be closed in 7 days.  
- Close message:  
  > Closing this PR because it has been stale for 7 additional days. Feel free to reopen or create a new PR when the work is ready.

You can implement this with `actions/stale@v9` in a separate workflow or as a scheduled job in your main workflow.[1][2][4]

***

### 1.2. CI-failure-based close (for your “failing PR” logic)

**Goal:** Close PRs that are clearly broken and not being fixed.

**Suggested policy:**

Close a PR if **all** of these are true:

1. **CI has been failing** for the latest commit:
   - At least one **required** check is failing.  
   - No successful run of the full required suite on the current head SHA.
2. **No recent attempt to fix**:
   - Last commit / last PR update is older than **14 days**.[3][10]
3. **No special exemption**:
   - PR does **not** have labels like: `experiment`, `draft`, `do-not-close`, `investigation`.

**Close comment template:**

> This PR has persistent CI failures and no updates for 14+ days. Closing to keep the queue clean.  
> If this work is still needed, please:  
> - Fix the failing checks, or  
> - Reopen / create a new PR with an updated branch.

You can make this stricter (e.g., 7 days) or looser (e.g., 30 days) depending on your team’s velocity.

***

### 1.3. Pre‑migration / cleanup close (optional)

If you ever do repo migrations or big restructures, you can add a one-off rule:

- Close all open PRs with:
  - No activity in **90 days**, and  
  - Not labeled `critical` / `release-blocker`.[10]

Comment:

> Closing as part of pre‑migration cleanup. This PR has been inactive for >90 days. Please reopen against the new repo/location if still needed.

***

## 2. Rules for moving files

Define **what** to move, **where**, and **when**.

### 2.1. When to move files

Trigger moves only when:

- PR is **merged** (`mode=merged`), or  
- PR is **closed without merge** (`mode=closed_unmerged`).  

Do **not** move files for open PRs.

***

### 2.2. Folder conventions

Assume a simple convention (adjust to your layout):

- Temporary / per-PR artifacts:  
  - `tmp/pr-{PR_NUMBER}/`  
  - `generated/pr-{PR_NUMBER}/`  
- Long-term archives:  
  - `archive/pr-{PR_NUMBER}/` (for closed, unmerged PRs)  
  - `merged/pr-{PR_NUMBER}/` (for merged PRs)  
- Review / quarantine (optional):  
  - `review/pr-{PR_NUMBER}/` (for suspicious or failing changes you want humans to inspect)

***

### 2.3. Move rules by PR state

#### A. PR merged (`mode=merged`)

**Goal:** Keep useful artifacts, but out of the way.

**Move:**

- From:  
  - `tmp/pr-{PR_NUMBER}/**`  
  - `generated/pr-{PR_NUMBER}/**`  
- To:  
  - `merged/pr-{PR_NUMBER}/`  

**Do not move:**

- Core source files (they’re already part of the merge).  
- Files outside the `tmp/` and `generated/` trees unless you explicitly tag them.

**Commit message:**

> Auto-move artifacts for merged PR #{PR_NUMBER}

***

#### B. PR closed without merge (`mode=closed_unmerged`)

**Goal:** Archive anything the PR created so it’s not left lying around.

**Move:**

- From:  
  - `tmp/pr-{PR_NUMBER}/**`  
  - `generated/pr-{PR_NUMBER}/**`  
  - Optionally: `review/pr-{PR_NUMBER}/**` if you use that for failing PRs  
- To:  
  - `archive/pr-{PR_NUMBER}/`  

**Commit message:**

> Auto-move artifacts for closed (unmerged) PR #{PR_NUMBER}

If your policy is “don’t keep anything from failed/abandoned PRs”, you can instead:

- Move to `archive/` and then have another job or manual step periodically **delete** old archives (e.g., >180 days).

***

#### C. PR failing CI but still open

You generally **do not move files yet**; you only:

- Debug / annotate CI.  
- Optionally label the PR as `ci-failing` or `needs-fix`.  

If you want a “quarantine” for clearly broken PRs that are being kept around for investigation:

- When a PR is marked `ci-failing` for >14 days, you can:
  - Move its `tmp/pr-{PR_NUMBER}/**` to `review/pr-{PR_NUMBER}/`  
  - Post a comment explaining why.

***

## 3. Concrete rules you can implement in your workflow

Below is a compact “policy block” you can translate into shell/JS/Python inside your `close-failing-prs` and `move-files` jobs.

### 3.1. Pseudocode: close-failing-prs

```text
IF github.event_name == "pull_request" AND action != "closed":
  FETCH PR info:
    - last_commit_date
    - labels
    - required_checks_status (all green or not)

  # Inactivity-based close (stale)
  IF last_activity_older_than(60 days) AND no_exempt_label:
    LABEL as "stale"
    POST stale comment
    IF last_activity_older_than(67 days):  # 60 + 7
      CLOSE PR with stale-close comment
      RETURN

  # CI-failure-based close
  IF required_checks_have_failures
     AND last_commit_older_than(14 days)
     AND no_exempt_label:
    CLOSE PR with CI-failure comment
    RETURN
```

Exempt labels example:

- `["work-in-progress", "WIP", "blocked", "do-not-close", "experiment", "investigation"]`

***

### 3.2. Pseudocode: move-files

```text
IF github.event_name == "pull_request" AND action == "closed":
  PR_NUMBER = pr.number
  MODE = (pr.merged ? "merged" : "closed_unmerged")

  IF MODE == "merged":
    DEST = "merged/pr-" + PR_NUMBER
  ELSE:
    DEST = "archive/pr-" + PR_NUMBER

  FOR pattern IN ["tmp/pr-" + PR_NUMBER + "/*", "generated/pr-" + PR_NUMBER + "/*"]:
    IF any_files_match(pattern):
      MOVE matching_files TO DEST

  IF any_files_were_moved:
    COMMIT & PUSH with message:
      "Auto-move artifacts for " + MODE + " PR #" + PR_NUMBER
```

You can extend this to:

- Move `review/pr-{PR_NUMBER}/**` to `archive/` as well.  
- Skip move if `DEST` already exists and is non-empty (to avoid duplicates).

***

## 4. Example snippet for your workflow (close + move)

You can drop this logic into your existing `close-failing-prs` and `move-files` jobs.

### Close-failing-prs (simplified)

```yaml
- name: Decide whether to close this PR
  run: |
    PR="${{ needs.analyze-pr.outputs.pr_number }}"
    REPO="${{ needs.analyze-pr.outputs.repo_full }}"

    # Get PR JSON
    gh pr view "$PR" --repo "$REPO" --json labels,updatedAt,commits > pr_info.json || true

    # Implement your policy here:
    # - parse last activity date
    # - check labels for exemptions
    # - check CI status (gh pr checks)
    #
    # If conditions met:
    #   gh pr close "$PR" --repo "$REPO" --comment "..."
    echo "Insert close logic here (see pseudocode above)"
```

### Move-files (with clear rules)

```yaml
- name: Move files for closed/merged PR
  run: |
    PR_NUMBER="${{ needs.analyze-pr.outputs.pr_number }}"
    MODE="${{ needs.analyze-pr.outputs.mode }}"

    if [ "$MODE" = "closed_unmerged" ]; then
      DEST="archive/pr-${PR_NUMBER}"
    else
      DEST="merged/pr-${PR_NUMBER}"
    fi

    mkdir -p "$DEST"

    for pattern in "tmp/pr-${PR_NUMBER}/*" "generated/pr-${PR_NUMBER}/*"; do
      if compgen -g "$pattern" > /dev/null; then
        mv $pattern "$DEST/" || true
      fi
    done
```

***

If you tell me:
- your actual folder layout (`tmp/`, `generated/`, etc.), and  
- how strict you want to be (e.g., 30 vs 60 days for stale, 7 vs 14 days for CI failures),  

I can give you exact shell/Node/Python code blocks ready to paste into your workflow.

การอ้างอิง:
[1] How to Configure Code Review Automation https://oneuptime.com/blog/post/2026-01-25-code-review-automation/view
[2] Automatically Close Stale PRs with GitHub Actions: The 2026 Tuning Guide ‣ 2026-09-03 https://yoo.be/close-stale-prs-github-actions-2026/
[3] Stale Issue Management | nodejs/help | DeepWiki https://deepwiki.com/nodejs/help/4.1-stale-issue-management
[4] openscience/.github/workflows/stale.yml at main · synthetic-sciences/openscience https://download.plaud.ai/synthetic-sciences/openscience/blob/main/.github/workflows/stale.yml
[5] Managing Stale Issues and Pull Requests with GitHub Actions https://tenthirtyam.org/dispatches/2026/04/13/managing-stale-issues-and-pull-requests-with-github-actions/
[6] Close stale pull requests/ issues after 60 days (#501) · 4bce51430e https://support.ostrachhelp.de/Mirrors/EOS/commit/4bce51430e2f5a0b2eba55cc308029b8d2f5be9e
[7] Close stale pull requests/ issues after 60 days (#501) · b4bc3d0eb2 https://support.ostrachhelp.de/Mirrors/EOS/commit/b4bc3d0eb2bdab1fb611245a90a95c0a3af5d6cb
[8] GitHub Workflows | lartpang/ZoomNeXt | DeepWiki https://deepwiki.com/lartpang/ZoomNeXt/8.2-github-workflows
[9] Issue Lifecycle Automation | Xinyuan-LilyGO/T-Embed-CC1101 | DeepWiki https://deepwiki.com/Xinyuan-LilyGO/T-Embed-CC1101/8.2-issue-lifecycle-automation
[10] The Complete Guide to Migrating to GitHub Enterprise Managed Users https://github.com/orgs/community/discussions/189383
[11] ci: create stale workflow by parkerbxyz · Pull Request #309 · actions/create-github-app-token https://github.com/actions/create-github-app-token/pull/309
[12] GitHub Actions Workflows | maravento/blackweb | DeepWiki https://deepwiki.com/maravento/blackweb/6.1-github-actions-workflows
[13] Trunk-Based Development Setup – Git Automation https://www.git-automation.com/git-workflow-architecture-branching-strategies/trunk-based-development-setup/
[14] GitHub Actions Workflows | deploymenttheory/terraform-provider-microsoft365 | DeepWiki https://deepwiki.com/deploymenttheory/terraform-provider-microsoft365/6.1-github-actions-workflows
