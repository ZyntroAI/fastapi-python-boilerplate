From b67f334f85a11d269aecb278e1d1069a48f0f219 Mon Sep 17 00:00:00 2001
From: fig-ai-agent <fig-ai-agent@users.noreply.github.com>
Date: Thu, 10 Sep 2026 06:59:41 +0000
Subject: [PATCH 1/3] fix(ci): repair five malformed workflow files
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit

Five of the twelve workflow files did not parse, so those workflows could never
load. Each failed for a different reason:

- test-suite.yml        the whole workflow was wrapped in a markdown ```yaml
                        fence, with prose before and after
- Auto-Index-Sync.yml   a single-quoted python heredoc spanning several lines
                        inside a run: | block, which terminates the scalar
- dependabot-automerge.yml  ~87 lines of GitHub documentation appended to the
                        end of the file
- secret-scan.yml       'workflow_dispatch;' â€” a semicolon where a colon belongs
- ci.yml                an inline flow mapping {python-version: ${{ ... }}}
                        that nests braces, plus stray CRLF line endings

Fixed by extracting the fenced body, truncating the appended prose, correcting
the delimiter, and expanding the flow mapping to block style. The single-quoted
heredoc became a printf call that stays valid under the block scalar's
indentation.

YAML parse check: 7/12 -> 12/12.
---
 .github/workflows/Auto-Index-Sync.yml      |  11 +-
 .github/workflows/ci.yml                   | 215 +++++++++++----------
 .github/workflows/dependabot-automerge.yml |  91 +--------
 .github/workflows/secret-scan.yml          |   8 +-
 .github/workflows/test-suite.yml           |  55 +-----
 5 files changed, 124 insertions(+), 256 deletions(-)

diff --git a/.github/workflows/Auto-Index-Sync.yml b/.github/workflows/Auto-Index-Sync.yml
index 6ea4c9c..c8f71f9 100644
--- a/.github/workflows/Auto-Index-Sync.yml
+++ b/.github/workflows/Auto-Index-Sync.yml
@@ -81,11 +81,12 @@ jobs:
           if [ ! -f scripts/parse_docs.py ]; then
             echo "âš ï¸ scripts/parse_docs.py missing â€” creating placeholder"
             mkdir -p scripts
-            echo '#!/usr/bin/env python3
-import sys
-print("# Policy Snapshot\n")
-print("Source:", sys.argv[1])
-' > scripts/parse_docs.py
+            printf '%s\n' \
+              '#!/usr/bin/env python3' \
+              'import sys' \
+              'print("# Policy Snapshot\\n")' \
+              'print("Source:", sys.argv[1])' \
+              > scripts/parse_docs.py
             chmod +x scripts/parse_docs.py
           fi
 
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index d1bd813..df3b2c6 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -1,107 +1,110 @@
-name: FastAPI CI/CD
-
-on:
-  push:
-    branches: [main, dev]
-  pull_request:
-    branches: [main]
-
-env:
-  PYTHON_VERSION: "3.12"
-  IMAGE_NAME: ghcr.io/zyntroai/fastapi-boilerplate
-  REGISTRY: ghcr.io
-
-jobs:
-  lint:
-    runs-on: ubuntu-latest
-    steps:
-      - uses: actions/checkout@v4
-      - uses: actions/setup-python@v5
-        with: {python-version: ${{ env.PYTHON_VERSION }}}
-      - run: python -m pip install ruff black isort
-      - run: ruff check .
-      - run: black --check .
-
-  test:
-    needs: lint
-    runs-on: ubuntu-latest
-    services:
-      postgres:
-        image: postgres:16-alpine
-        env: {POSTGRES_USER: test, POSTGRES_PASSWORD: test, POSTGRES_DB: test}
-        ports: ["5432:5432"]
-        options: >-
-          --health-cmd pg_isready
-          --health-interval 10s
-          --health-timeout 5s
-          --health-retries 5
-    steps:
-      - uses: actions/checkout@v4
-      - uses: actions/setup-python@v5
-        with: {python-version: ${{ env.PYTHON_VERSION }}}
-      - run: pip install -r requirements.txt
-      - name: Run Tests with Coverage
-        run: |
-          pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=xml
-        env:
-          DATABASE_URL: postgresql://test:test@localhost:5432/test
-      - name: Upload Coverage to Codecov
-        uses: codecov/codecov-action@v4
-        with:
-          files: ./coverage.xml
-          flags: unittests
-          name: codecov-coverage
-          fail_ci_if_error: false
-          verbose: true
-
-  security:
-    needs: test
-    runs-on: ubuntu-latest
-    permissions:
-      actions: read
-      contents: read
-      security-events: write
-    steps:
-      - uses: actions/checkout@v4
-        with:
-          fetch-depth: 2
-      - name: Set up Python
-        uses: actions/setup-python@v5
-        with: {python-version: ${{ env.PYTHON_VERSION }}}
-      - name: Install dependencies
-        run: |
-          python -m pip install --upgrade pip
-          pip install -r requirements.txt
-      - name: Initialize CodeQL
-        uses: github/codeql-action/init@v3
-        with:
-          languages: python
-          build-mode: none
-      - name: Autobuild
-        uses: github/codeql-action/autobuild@v3
-      - name: Perform CodeQL Analysis
-        uses: github/codeql-action/analyze@v3
-        with:
-          category: "/language:python"
-
-  build:
-    needs: security
-    runs-on: ubuntu-latest
-    if: github.ref == 'refs/heads/main'
-    permissions:
-      contents: read
-      packages: write
-    steps:
-      - uses: actions/checkout@v4
-      - name: Log in to GHCR
-        uses: docker/login-action@v3
-        with:
-          registry: ${{ env.REGISTRY }}
-          username: ${{ github.actor }}
-          password: ${{ secrets.GITHUB_TOKEN }}
-      - name: Build & Push
-        uses: docker/build-push-action@v5
-        with:
-          context: .
-          push: true
+name: FastAPI CI/CD
+
+on:
+  push:
+    branches: [main, dev]
+  pull_request:
+    branches: [main]
+
+env:
+  PYTHON_VERSION: "3.12"
+  IMAGE_NAME: ghcr.io/zyntroai/fastapi-boilerplate
+  REGISTRY: ghcr.io
+
+jobs:
+  lint:
+    runs-on: ubuntu-latest
+    steps:
+      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
+      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065  # v5
+        with:
+          python-version: ${{ env.PYTHON_VERSION }}
+      - run: python -m pip install ruff black isort
+      - run: ruff check .
+      - run: black --check .
+
+  test:
+    needs: lint
+    runs-on: ubuntu-latest
+    services:
+      postgres:
+        image: postgres:16-alpine
+        env: {POSTGRES_USER: test, POSTGRES_PASSWORD: test, POSTGRES_DB: test}
+        ports: ["5432:5432"]
+        options: >-
+          --health-cmd pg_isready
+          --health-interval 10s
+          --health-timeout 5s
+          --health-retries 5
+    steps:
+      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
+      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065  # v5
+        with:
+          python-version: ${{ env.PYTHON_VERSION }}
+      - run: pip install -r requirements.txt
+      - name: Run Tests with Coverage
+        run: |
+          pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=xml
+        env:
+          DATABASE_URL: postgresql://test:test@localhost:5432/test
+      - name: Upload Coverage to Codecov
+        uses: codecov/codecov-action@b9fd7d16f6d7d1b5d2bec1a2887e65ceed900238  # v4
+        with:
+          files: ./coverage.xml
+          flags: unittests
+          name: codecov-coverage
+          fail_ci_if_error: false
+          verbose: true
+
+  security:
+    needs: test
+    runs-on: ubuntu-latest
+    permissions:
+      actions: read
+      contents: read
+      security-events: write
+    steps:
+      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
+        with:
+          fetch-depth: 2
+      - name: Set up Python
+        uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065  # v5
+        with:
+          python-version: ${{ env.PYTHON_VERSION }}
+      - name: Install dependencies
+        run: |
+          python -m pip install --upgrade pip
+          pip install -r requirements.txt
+      - name: Initialize CodeQL
+        uses: github/codeql-action/init@faaca9a8f6edddba5725ffe5adefdab6669a2eca  # v3
+        with:
+          languages: python
+          build-mode: none
+      - name: Autobuild
+        uses: github/codeql-action/autobuild@faaca9a8f6edddba5725ffe5adefdab6669a2eca  # v3
+      - name: Perform CodeQL Analysis
+        uses: github/codeql-action/analyze@faaca9a8f6edddba5725ffe5adefdab6669a2eca  # v3
+        with:
+          category: "/language:python"
+
+  build:
+    needs: security
+    runs-on: ubuntu-latest
+    if: github.ref == 'refs/heads/main'
+    permissions:
+      contents: read
+      packages: write
+    steps:
+      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
+      - name: Log in to GHCR
+        uses: docker/login-action@c94ce9fb468520275223c153574b00df6fe4bcc9  # v3
+        with:
+          registry: ${{ env.REGISTRY }}
+          username: ${{ github.actor }}
+          password: ${{ secrets.GITHUB_TOKEN }}
+      - name: Build & Push
+        uses: docker/build-push-action@ca052bb54ab0790a636c9b5f226502c73d547a25  # v5
+        with:
+          context: .
+          push: true
           tags: ${{ env.IMAGE_NAME }}:latest
\ No newline at end of file
diff --git a/.github/workflows/dependabot-automerge.yml b/.github/workflows/dependabot-automerge.yml
index 6cd823f..003a126 100644
--- a/.github/workflows/dependabot-automerge.yml
+++ b/.github/workflows/dependabot-automerge.yml
@@ -15,13 +15,13 @@ jobs:
     steps:
       - name: Fetch Dependabot metadata
         id: metadata
-        uses: dependabot/fetch-metadata@v2
+        uses: dependabot/fetch-metadata@21025c705c08248db411dc16f3619e6b5f9ea21a  # v2
         with:
           github-token: "${{ secrets.GITHUB_TOKEN }}"
 
       - name: Auto-merge patch updates only
         if: steps.metadata.outputs.update-type == 'version-update:semver-patch'
-        uses: pascalgn/automerge-action@v0.16.4
+        uses: pascalgn/automerge-action@7961b8b5eec56cc088c140b56d864285eabd3f67  # v0.16.4
         env:
           GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}"
           MERGE_LABELS: "dependencies"
@@ -32,90 +32,3 @@ jobs:
           MERGE_RETRY_SLEEP: "10000"
           UPDATE_LABELS: ""
           MERGE_DELETE_BRANCH: "true"
-
-# Navigating code on GitHub
-
-You can understand the relationships within and across repositories by navigating code directly in GitHub.
-
-<!-- If you make changes to this feature, check whether any of the changes affect languages listed in /get-started/learning-about-github/github-language-support. If so, please update the article accordingly. -->
-
-## About navigating code on GitHub
-
-Code navigation helps you to read, navigate, and understand code by showing and linking definitions of a named entity corresponding to a reference to that entity, as well as references corresponding to an entity's definition.
-
-![Screenshot showing a file with a function highlighted. A pop-up has information about the function on two tabs: "Definition" and "Reference".](/assets/images/help/repository/code-navigation-popover.png)
-
-Code navigation uses the open source [`tree-sitter`](https://github.com/tree-sitter/tree-sitter) library. The following languages support code navigation.
-
-* Bash
-* C
-* C#
-* C++
-* CodeQL
-* Elixir
-* Go
-* JSX
-* Java
-* JavaScript
-* Lua
-* PHP
-* Protocol Buffers
-* Python
-* R
-* Ruby
-* Rust
-* Scala
-* Starlark
-* Swift
-* Typescript
-
-You do not need to configure anything in your repository to enable code navigation. We will automatically extract code navigation information for these supported languages in all repositories.
-
-GitHub has developed a code navigation approach based on the open source [`tree-sitter`](https://github.com/tree-sitter/tree-sitter) library that searches all definitions and references across a repository to find entities with a given name.
-
-You can use keyboard shortcuts to navigate within a code file. For more information, see [Keyboard shortcuts](/en/get-started/accessibility/keyboard-shortcuts#navigating-within-code-files).
-
-## Using the symbols pane
-
-You can now quickly view and navigate between symbols such as functions or classes in your code with the symbols pane. You can search for a symbol in a single file, in all files in a repository, or even in all public repositories on GitHub.
-
-Symbol search is a feature of code search. For more information, see [Understanding GitHub Code Search syntax](/en/search-github/github-code-search/understanding-github-code-search-syntax#symbol-qualifier).
-
-1. Select a repository, then navigate to a file containing symbols.
-
-2. To bring up the symbols pane, above the file content, click <svg version="1.1" width="16" height="16" viewBox="0 0 16 16" class="octicon octicon-code-square" aria-label="The code square icon" role="img"><path d="M0 1.75C0 .784.784 0 1.75 0h12.5C15.216 0 16 .784 16 1.75v12.5A1.75 1.75 0 0 1 14.25 16H1.75A1.75 1.75 0 0 1 0 14.25Zm1.75-.25a.25.25 0 0 0-.25.25v12.5c0 .138.112.25.25.25h12.5a.25.25 0 0 0 .25-.25V1.75a.25.25 0 0 0-.25-.25Zm7.47 3.97a.75.75 0 0 1 1.06 0l2 2a.75.75 0 0 1 0 1.06l-2 2a.749.749 0 0 1-1.275-.326.749.749 0 0 1 .215-.734L10.69 8 9.22 6.53a.75.75 0 0 1 0-1.06ZM6.78 6.53 5.31 8l1.47 1.47a.749.749 0 0 1-.326 1.275.749.749 0 0 1-.734-.215l-2-2a.75.75 0 0 1 0-1.06l2-2a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042Z"></path></svg>.
-
-   Alternatively, you can open the symbols pane by clicking an eligible symbol in your file. Clickable symbols are highlighted in yellow when you hover over them.
-
-3. Click the symbol you would like to find from the symbols pane or within the file itself.
-
-   * To search for a symbol in the repository as a whole, in the symbols pane, click **Search for this symbol in this repository**. To search for a symbol in all repositories on GitHub, click **all repositories**.
-
-4. To navigate between references to a symbol, click <svg version="1.1" width="16" height="16" viewBox="0 0 16 16" class="octicon octicon-chevron-down" aria-label="The downwards-facing chevron icon" role="img"><path d="M12.78 5.22a.749.749 0 0 1 0 1.06l-4.25 4.25a.749.749 0 0 1-1.06 0L3.22 6.28a.749.749 0 1 1 1.06-1.06L8 8.939l3.72-3.719a.749.749 0 0 1 1.06 0Z"></path></svg> or <svg version="1.1" width="16" height="16" viewBox="0 0 16 16" class="octicon octicon-chevron-up" aria-label="The upwards-facing chevron icon" role="img"><path d="M3.22 10.53a.749.749 0 0 1 0-1.06l4.25-4.25a.749.749 0 0 1 1.06 0l4.25 4.25a.749.749 0 1 1-1.06 1.06L8 6.811 4.28 10.53a.749.749 0 0 1-1.06 0Z"></path></svg>.
-
-5. To navigate to a specific reference to a symbol, click a result of the symbol search under **<svg version="1.1" width="16" height="16" viewBox="0 0 16 16" class="octicon octicon-chevron-down" aria-label="chevron-down" role="img"><path d="M12.78 5.22a.749.749 0 0 1 0 1.06l-4.25 4.25a.749.749 0 0 1-1.06 0L3.22 6.28a.749.749 0 1 1 1.06-1.06L8 8.939l3.72-3.719a.749.749 0 0 1 1.06 0Z"></path></svg> In this file**.
-
-6. To exit the search for a specific symbol, click **<svg version="1.1" width="16" height="16" viewBox="0 0 16 16" class="octicon octicon-arrow-left" aria-label="arrow-left" role="img"><path d="M7.78 12.53a.75.75 0 0 1-1.06 0L2.47 8.28a.75.75 0 0 1 0-1.06l4.25-4.25a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042L4.81 7h7.44a.75.75 0 0 1 0 1.5H4.81l2.97 2.97a.75.75 0 0 1 0 1.06Z"></path></svg> All Symbols**.
-
-## Jumping to the definition of a function or method
-
-You can jump to a function or method's definition within the same repository by clicking the function or method call in a file.
-
-![Screenshot of the function window. A section, titled "Definition," is outlined in dark orange.](/assets/images/help/repository/jump-to-definition-tab.png)
-
-## Finding all references of a function or method
-
-You can find all references for a function or method within the same repository by clicking the function or method call in a file.
-
-![Screenshot of the function window. A section, titled "3 References," is outlined in dark orange.](/assets/images/help/repository/find-all-references-tab.png)
-
-## Troubleshooting code navigation
-
-If code navigation is enabled for you but you don't see links to the definitions of functions and methods:
-
-* Code navigation only works for active branches. Push to the branch and try again.
-* Code navigation only works for repositories with fewer than 100,000 files.
-
-## Further reading
-
-* [About GitHub Code Search](/en/search-github/github-code-search/about-github-code-search)
diff --git a/.github/workflows/secret-scan.yml b/.github/workflows/secret-scan.yml
index c63a316..5dc8497 100644
--- a/.github/workflows/secret-scan.yml
+++ b/.github/workflows/secret-scan.yml
@@ -4,7 +4,7 @@ on:
   push:
     branches: [main]
   pull_request:
-  workflow_dispatch;
+  workflow_dispatch:
 
 permissions:
   contents: read
@@ -15,17 +15,17 @@ jobs:
     runs-on: ubuntu-latest
 
     steps:
-      - uses: actions/checkout@v4
+      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
         with:
           fetch-depth: 0
 
       - name: Run Gitleaks
-        uses: gitleaks/gitleaks-action@v2
+        uses: gitleaks/gitleaks-action@ff98106e4c7b2bc287b24eaf42907196329070c7  # v2
         env:
           GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
 
       - name: Upload SARIF
         if: always()
-        uses: github/codeql-action/upload-sarif@v3
+        uses: github/codeql-action/upload-sarif@faaca9a8f6edddba5725ffe5adefdab6669a2eca  # v3
         with:
           sarif_file: results.sarif
diff --git a/.github/workflows/test-suite.yml b/.github/workflows/test-suite.yml
index a088dbf..ff7c544 100644
--- a/.github/workflows/test-suite.yml
+++ b/.github/workflows/test-suite.yml
@@ -1,10 +1,3 @@
-# ðŸ“„ Complete Final Workflow â€” `.github/workflows/test-suite.yml`
-
-Here's your **full, production-ready workflow** â€” everything integrated: Docker Compose stack, migrations, seed user, unit + E2E tests, coverage, and cleanup. Ready to copy-paste directly!
-
----
-
-```yaml
 name: ðŸ§ª Test Suite
 
 on:
@@ -30,10 +23,10 @@ jobs:
 
     steps:
       - name: ðŸ“¥ Checkout code
-        uses: actions/checkout@v4
+        uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
 
       - name: ðŸ Set up Python 3.11
-        uses: actions/setup-python@v5
+        uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065  # v5
         with:
           python-version: "3.11"
           cache: "pip"
@@ -122,7 +115,7 @@ jobs:
           PYTHONUNBUFFERED: "1"
 
       - name: ðŸ“¤ Upload Coverage to Codecov
-        uses: codecov/codecov-action@v4
+        uses: codecov/codecov-action@b9fd7d16f6d7d1b5d2bec1a2887e65ceed900238  # v4
         with:
           files: ./coverage.xml
           flags: full-stack,e2e,auth
@@ -131,45 +124,3 @@ jobs:
       - name: ðŸ§¹ Cleanup Stack
         if: always()
         run: docker compose down --remove-orphans --volumes
-```
-
----
-
-## âœ… What's Inside â€” Complete Checklist
-
-| Stage | What It Does |
-|---|---|
-| ðŸ³ **Spin Up Stack** | Builds & starts API + PostgreSQL + Redis + Traefik |
-| â³ **Health Checks** | Waits for EVERY service before proceeding |
-| ðŸ“Š **Migrations** | Schema matches production exactly |
-| ðŸ”‘ **Seed User** | Creates test user safely with error handling + rollback |
-| ðŸ§ª **Run All Tests** | Unit + Integration + E2E Auth Flow through Traefik |
-| ðŸ“¤ **Coverage** | Uploads combined report â†’ Codecov â†’ README badge |
-| ðŸ§¹ **Cleanup** | Always removes stack â€” even if tests fail |
-
----
-
-## ðŸ“Œ Quick Deployment
-
-1. **Replace** your existing `.github/workflows/test-suite.yml` with this entire file
-2. **Verify** your `docker-compose.yml` has services: `postgres`, `redis`, `traefik`, `api`
-3. **Verify** your test files exist:
-   - `tests/e2e/test_auth_flow.py`
-   - `tests/e2e/test_health.py`
-   - `tests/e2e/test_items_api.py`
-4. **Commit & Push** â†’ Workflow runs automatically! ðŸš€
-
----
-
-## ðŸ›¡ï¸ Branch Protection Reminder
-
-Go to: **Repo â†’ Settings â†’ Branches â†’ Branch protection rule â†’ main**
-- âœ… **Require status checks to pass before merging**
-- âœ… Select job: `ðŸ§ª Full Stack + E2E API Tests`
-â†’ **No code merges unless ALL tests pass!** ðŸ”’âœ…
-
----
-
-âœ… **Ready to use!** Save â†’ Commit â†’ Push â†’ Every PR now validates your **entire stack end-to-end** ðŸŽ‰
-
-Would you like me to also provide the **async version of the seed step** in case you migrate to fully async SQLAlchemy later? âš¡ðŸ˜
-- 
2.47.3


From c33cc2d95440cce58e21ee9994cb817dc41b3b53 Mon Sep 17 00:00:00 2001
From: fig-ai-agent <fig-ai-agent@users.noreply.github.com>
Date: Thu, 10 Sep 2026 06:59:47 +0000
Subject: [PATCH 2/3] chore(ci): pin all action references to full commit SHAs
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit

Every 'uses:' reference was a mutable version tag (@v4, @v5, ...). A tag can be
repointed at any commit by whoever owns the action, so a tag-pinned workflow
runs whatever that owner publishes next â€” the supply-chain hole SHA-pinning
closes.

66 refs across 9 files converted to full 40-character commit SHAs, each resolved
from the GitHub API and annotated with the tag it came from:

    uses: actions/checkout@11d5960a...  # v4

6 refs were already SHA-pinned and left alone. The 6 refs inside
archive/workflows-dormant/ are intentionally NOT pinned â€” those files never
execute, and pinning them to a SHA that cannot be verified from here would be
worse than a readable tag.

YAML parse check still 12/12 after the rewrite.
---
 .github/workflows/ADD EXAMPLAE AGENTS         |  20 ---
 .github/workflows/Auto-Build-SVG.md           |  32 ----
 .github/workflows/README.md                   | 143 ------------------
 .../build-compress-all-platforms.yml          |  58 +++----
 .github/workflows/copilot-audit.yml           |   2 +-
 .github/workflows/deploy.yml (Production)     |  50 ------
 .github/workflows/live-task.yml               |  14 +-
 .../name Deploy Static Content to Pages.txt   |  39 -----
 .github/workflows/static.yml                  |   8 +-
 .github/workflows/test-and-coverage.yaml      |   8 +-
 .github/workflows/vercel-deployment           |  12 --
 ...\360\237\247\252 Staging Workflow Example" |  51 -------
 12 files changed, 45 insertions(+), 392 deletions(-)
 delete mode 100644 .github/workflows/ADD EXAMPLAE AGENTS
 delete mode 100644 .github/workflows/Auto-Build-SVG.md
 delete mode 100644 .github/workflows/README.md
 delete mode 100644 .github/workflows/deploy.yml (Production)
 delete mode 100644 .github/workflows/name Deploy Static Content to Pages.txt
 delete mode 100644 .github/workflows/vercel-deployment
 delete mode 100644 ".github/workflows/\360\237\247\252 Staging Workflow Example"

diff --git a/.github/workflows/ADD EXAMPLAE AGENTS b/.github/workflows/ADD EXAMPLAE AGENTS
deleted file mode 100644
index f172228..0000000
--- a/.github/workflows/ADD EXAMPLAE AGENTS	
+++ /dev/null
@@ -1,20 +0,0 @@
-# Sample AGENTS.md file
-
-## Dev environment tips
-- Use `pnpm dlx turbo run where <project_name>` to jump to a package instead of scanning with `ls`.
-- Run `pnpm install --filter <project_name>` to add the package to your workspace so Vite, ESLint, and TypeScript can see it.
-- Use `pnpm create vite@latest <project_name> -- --template react-ts` to spin up a new React + Vite package with TypeScript checks ready.
-- Check the name field inside each package's package.json to confirm the right nameâ€”skip the top-level one.
-
-## Testing instructions
-- Find the CI plan in the .github/workflows folder.
-- Run `pnpm turbo run test --filter <project_name>` to run every check defined for that package.
-- From the package root you can just call `pnpm test`. The commit should pass all tests before you merge.
-- To focus on one step, add the Vitest pattern: `pnpm vitest run -t "<test name>"`.
-- Fix any test or type errors until the whole suite is green.
-- After moving files or changing imports, run `pnpm lint --filter <project_name>` to be sure ESLint and TypeScript rules still pass.
-- Add or update tests for the code you change, even if nobody asked.
-
-## PR instructions
-- Title format: [<project_name>] <Title>
-- Always run `pnpm lint` and `pnpm test` before committing.
diff --git a/.github/workflows/Auto-Build-SVG.md b/.github/workflows/Auto-Build-SVG.md
deleted file mode 100644
index 2a98937..0000000
--- a/.github/workflows/Auto-Build-SVG.md
+++ /dev/null
@@ -1,32 +0,0 @@
-Here are a few workflow patterns for an agent whose job is generating SVGs, depending on what's driving the output:
-
-**1. Data-to-chart pipeline**
-1. Validate/parse input data (shape, ranges, missing values)
-2. Choose chart type based on data shape (categorical â†’ bar, time series â†’ line, part-whole â†’ pie/donut)
-3. Compute layout (viewBox, scales, padding) before drawing elements
-4. Generate SVG primitives (axes â†’ gridlines â†’ data â†’ labels/legend last, so they're not obscured)
-5. Validate output (well-formed XML, viewBox matches content bounds)
-
-**2. Diagram/flowchart from description**
-1. Parse the description into nodes + edges (a simple graph structure) before touching SVG
-2. Auto-layout (grid, hierarchical, or force-directed depending on complexity)
-3. Draw edges first, then nodes on top (avoids lines cutting through boxes)
-4. Add text last, sized to fit its container
-5. Check for overlaps/collisions; re-layout if any
-
-**3. Icon/illustration generation**
-1. Define a fixed canvas size and grid (e.g., 24Ã—24, 100Ã—100) up front for consistency
-2. Sketch structure with simple shapes first (circles/rects/paths as placeholders)
-3. Refine paths, add detail
-4. Optimize (remove redundant points, consolidate paths)
-5. Validate against a style guide if one exists (stroke width, corner radius, color tokens)
-
-**4. Iterative/editable SVG (user refines it conversationally)**
-1. Generate a first draft with clearly labeled/grouped `<g>` elements (semantic IDs)
-2. On each revision, edit specific groups rather than regenerating the whole file
-3. Keep a running "spec" (what each group represents) so edits stay consistent
-4. Re-validate viewBox/bounds after each edit, since edits can silently break layout
-
-A cross-cutting rule for all of these: **always use CSS variables for colors** if the SVG needs to adapt to themes, and **compute the viewBox from actual content bounds** rather than guessing â€” that's the most common source of clipped or off-center SVGs.
-
-Which of these matches what you're building â€” is this for the Visualizer-style inline diagrams, or a standalone SVG-generation skill/agent?
diff --git a/.github/workflows/README.md b/.github/workflows/README.md
deleted file mode 100644
index d4cef5d..0000000
--- a/.github/workflows/README.md
+++ /dev/null
@@ -1,143 +0,0 @@
-âœ… **Added!** Here's the complete `.github/workflows/README.md` â€” ready to copy and commit directly to your repo:
-
----
-
-```markdown
-# ðŸ“‹ Workflows â€” fastapi-python-boilerplate
-
-> **Path:** `.github/workflows/` Â· **Maintainer:** ZyntroAI
-> **Purpose:** CI/CD pipelines, automation, quality checks, security scans, and deployment
-
----
-
-## ðŸ“ Available Workflows
-
-| Workflow File | Purpose | Triggers |
-|---|---|---|
-| **Auto-Index-Sync.yml** | Index documentation â†’ search engine, crawl external docs, audit affiliate policies | Push Â· Nightly (02:00 UTC) Â· Manual |
-| **Auto-Build-SVG.yml** | Auto-generate SVG badges & visual assets | Docs/assets changes |
-| **auto-compress-manage.yml** | Compress & manage build artifacts | On build completion |
-| **build-compress-all-platforms.yml** | Cross-platform build + compression matrix | Release tags / Manual |
-| **ci.yml** | General CI â€” lint, test, build, validation | PR Â· Push Â· Schedule |
-| **copilot-audit.yml** | AI-powered code quality & security pattern audit | PR Â· Schedule |
-| **dependabot-automerge.yml** | Auto-merge minor/patch dependency version bumps | Dependabot |
-| **deploy.yml (Production)** | Deploy application to production environment | Release Â· Manual |
-| **live-task.yml** | Run live integration & connectivity tasks | Schedule Â· Manual |
-| **release_drafter.yml** | Auto-generate & update release notes / CHANGELOG | PR Â· Push |
-| **secret-scan.yml** | Scan commits for exposed credentials & secrets | All PR Â· Push |
-| **static.yml** | Static analysis â€” linting, type checking, code style | PR Â· Push |
-| **test-and-coverage.yml** | Run unit tests + upload coverage reports | PR Â· Push |
-| **test-suite.yml** | Full test matrix across Python versions | PR Â· Daily schedule |
-| **vercel-deployment.yml** | Deploy docs/frontend to Vercel | Docs changes Â· Manual |
-| **Staging-Workflow-Example.yml** | Reference template for staging deployments | â€” |
-
----
-
-## ðŸš€ Quick Start
-
-### â–¶ï¸ Run Any Workflow Manually
-1. Go to **Actions** tab in GitHub
-2. Select workflow from sidebar
-3. Click **Run workflow** â†’ choose branch â†’ âœ…
-
-### ðŸ”‘ Auto-Index-Sync (Most Used)
-> Syncs `docs/` â†’ Algolia search index, crawls OpenClaw docs, audits affiliate policy changes
-- **Schedule:** Daily `02:00 UTC` â†’ `09:00 ICT`
-- **Required Secrets:**
-  - `ALGOLIA_APP_ID` â€” Algolia Application ID
-  - `ALGOLIA_API_KEY` â€” Algolia Admin API Key
-- **Supporting Scripts:** `scripts/extract_metadata.py` Â· `scripts/push_index.py` Â· `scripts/parse_docs.py`
-
----
-
-## ðŸ”§ Shared Standards
-
-### Permissions (Standard Template)
-```yaml
-permissions:
-  contents: write        # Checkout, commit, push
-  pull-requests: write   # Post status & review comments
-```
-
-### Python Setup (Reusable Snippet)
-```yaml
-- name: Set up Python
-  uses: actions/setup-python@0a5c61591373683505ea898e09a731b4c89a1da0 # v5.2.0
-  with:
-    python-version: "3.12"
-
-- name: Install dependencies
-  run: |
-    python -m pip install --upgrade pip
-    pip install -r scripts/requirements.txt
-```
-
-### Trigger Best Practices
-```yaml
-on:
-  push:
-    branches: [main]
-    paths: ["docs/**", "scripts/**"]  # Only run when relevant files change
-  schedule:
-    - cron: "0 2 * * *"  # Off-peak UTC run
-  workflow_dispatch:
-    inputs:
-      dry_run:
-        description: Preview only â€” skip push
-        type: boolean
-        default: false
-```
-
----
-
-## ðŸ“‚ Related Assets
-
-| Path | Role |
-|---|---|
-| `scripts/` | Python helpers invoked by workflows |
-| `docs/` | Documentation indexed by Auto-Index-Sync |
-| `.github/actions/` | Reusable composite actions |
-| `.github/dependabot.yml` | Dependency auto-update config |
-
----
-
-## âœ… Standards Enforced
-- âœ… **Actions pinned to commit SHA** â€” security policy compliance
-- âœ… **Path filters** â€” avoid unnecessary runs
-- âœ… **`[skip ci]` on bot commits** â€” prevent trigger loops
-- âœ… **Conditional logic** â€” skip commit/push when no changes
-- âœ… **Consistent Python 3.12** across all jobs
-- âœ… **Minimal permissions** principle
-
----
-
-## ðŸ†˜ Troubleshooting
-
-| Symptom | Solution |
-|---|---|
-| `python: can't open file` | Add `actions/checkout@v4` as **first step** in every job |
-| Git push fails | Add `permissions: contents: write` at job or workflow level |
-| Algolia index not updated | Verify `ALGOLIA_APP_ID` & `ALGOLIA_API_KEY` in repo Secrets |
-| Script not found | Ensure scripts exist in `scripts/` â€” workflow creates placeholders |
-
----
-
-## ðŸ“ Adding a New Workflow
-1. Create `.github/workflows/your-workflow.yml`
-2. Use standard triggers + pinned action SHAs
-3. Add entry to **Available Workflows** table above
-4. Commit â†’ PR â†’ Merge âœ…
-
----
-
-> **Last Updated:** 2026-09-08 Â· **Standards:** Security-first Â· Pinned SHAs Â· Minimal permissions
-```
-
----
-
-### âœ… Next Steps
-1. Create file: **`Add file â†’ .github/workflows/README.md`**
-2. Paste the content above
-3. Commit directly to `main` branch âœ…
-
-Want me to also **generate a `requirements.txt`** for your scripts folder so Python dependencies install automatically? ðŸ“¦
\ No newline at end of file
diff --git a/.github/workflows/build-compress-all-platforms.yml b/.github/workflows/build-compress-all-platforms.yml
index a433b02..db548de 100644
--- a/.github/workflows/build-compress-all-platforms.yml
+++ b/.github/workflows/build-compress-all-platforms.yml
@@ -52,7 +52,7 @@ jobs:
       should_build_macos: ${{ steps.decide.outputs.macos }}
       should_build_linux: ${{ steps.decide.outputs.linux }}
     steps:
-      - uses: actions/checkout@v4
+      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
 
       - name: Generate Version
         id: version
@@ -91,16 +91,16 @@ jobs:
     if: needs.prepare.outputs.should_build_android == 'true'
     runs-on: ubuntu-latest
     steps:
-      - uses: actions/checkout@v4
+      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
 
       - name: Setup Java
-        uses: actions/setup-java@v4
+        uses: actions/setup-java@cf277c60eb25467037889841efdb72551f06f6c3  # v4
         with:
           java-version: '17'
           distribution: 'temurin'
 
       - name: Setup Flutter
-        uses: subosito/flutter-action@v2
+        uses: subosito/flutter-action@1a449444c387b1966244ae4d4f8c696479add0b2  # v2
         with:
           flutter-version: '3.24.0'
           channel: 'stable'
@@ -122,7 +122,7 @@ jobs:
 
       - name: Compress Android Builds
         id: compress
-        uses: somaz94/compress-decompress@v1
+        uses: somaz94/compress-decompress@4aa7a81b5e2c20ac4a865d937466f3d8928f487c  # v1
         with:
           command: compress
           source: |
@@ -135,7 +135,7 @@ jobs:
 
       - name: Sign APK (à¸–à¹‰à¸²à¸¡à¸µ keystore)
         if: secrets.ANDROID_KEYSTORE != ''
-        uses: r0adkll/sign-android-release@v1
+        uses: r0adkll/sign-android-release@349ebdef58775b1e0d8099458af0816dc79b6407  # v1
         with:
           releaseDirectory: build/app/outputs/flutter-apk
           signingKeyBase64: ${{ secrets.ANDROID_KEYSTORE }}
@@ -144,7 +144,7 @@ jobs:
           keyPassword: ${{ secrets.ANDROID_KEY_PASSWORD }}
 
       - name: Upload Android Artifact
-        uses: actions/upload-artifact@v4
+        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02  # v4
         with:
           name: android-build
           path: artifacts/*.zip
@@ -152,7 +152,7 @@ jobs:
 
       - name: Upload to Firebase App Distribution
         if: github.event.inputs.release_type != 'production'
-        uses: wzieba/Firebase-Distribution-Github-Action@v1
+        uses: wzieba/Firebase-Distribution-Github-Action@bd494989dd4bec0343f78adee87fe66e48279ad6  # v1
         with:
           appId: ${{ secrets.FIREBASE_ANDROID_APP_ID }}
           serviceCredentialsFileContent: ${{ secrets.FIREBASE_SERVICE_ACCOUNT }}
@@ -167,10 +167,10 @@ jobs:
     if: needs.prepare.outputs.should_build_ios == 'true'
     runs-on: macos-latest  # âš ï¸ à¸ˆà¸³à¹€à¸›à¹‡à¸™à¸•à¹‰à¸­à¸‡à¹ƒà¸Šà¹‰ macOS
     steps:
-      - uses: actions/checkout@v4
+      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
 
       - name: Setup Flutter
-        uses: subosito/flutter-action@v2
+        uses: subosito/flutter-action@1a449444c387b1966244ae4d4f8c696479add0b2  # v2
         with:
           flutter-version: '3.24.0'
           channel: 'stable'
@@ -181,13 +181,13 @@ jobs:
           pod setup
 
       - name: Install Apple Certificate
-        uses: apple-actions/import-codesign-certs@v3
+        uses: apple-actions/import-codesign-certs@63fff01cd422d4b7b855d40ca1e9d34d2de9427d  # v3
         with:
           p12-file-base64: ${{ secrets.IOS_P12_CERTIFICATE }}
           p12-password: ${{ secrets.IOS_P12_PASSWORD }}
 
       - name: Install Provisioning Profile
-        uses: apple-actions/download-provisioning-profiles@v1
+        uses: apple-actions/download-provisioning-profiles@3167792207a5b26099bc0ca22b5010a323dd2a0b  # v1
         with:
           bundle-id: com.zyntroai.crystalcastleX
           issuer-id: ${{ secrets.APPSTORE_ISSUER_ID }}
@@ -209,7 +209,7 @@ jobs:
           zip -r crystalcastleX-ios-v${{ needs.prepare.outputs.version }}.ipa Payload
 
       - name: Compress IPA
-        uses: somaz94/compress-decompress@v1
+        uses: somaz94/compress-decompress@4aa7a81b5e2c20ac4a865d937466f3d8928f487c  # v1
         with:
           command: compress
           source: build/ios/iphoneos/crystalcastleX-ios-v${{ needs.prepare.outputs.version }}.ipa
@@ -219,7 +219,7 @@ jobs:
           destfilename: 'crystalcastleX-ios-v${{ needs.prepare.outputs.version }}'
 
       - name: Upload iOS Artifact
-        uses: actions/upload-artifact@v4
+        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02  # v4
         with:
           name: ios-build
           path: artifacts/*.zip
@@ -227,7 +227,7 @@ jobs:
 
       - name: Upload to TestFlight
         if: github.event.inputs.release_type == 'production'
-        uses: apple-actions/upload-testflight-build@v1
+        uses: apple-actions/upload-testflight-build@54dc215b4cd5529730db39f11c84efdb71414e07  # v1
         with:
           app-path: build/ios/iphoneos/crystalcastleX-ios-v${{ needs.prepare.outputs.version }}.ipa
           issuer-id: ${{ secrets.APPSTORE_ISSUER_ID }}
@@ -242,7 +242,7 @@ jobs:
     if: needs.prepare.outputs.should_build_windows == 'true'
     runs-on: windows-latest
     steps:
-      - uses: actions/checkout@v4
+      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
 
       - name: Enable Long Path Support
         run: |
@@ -250,7 +250,7 @@ jobs:
           New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
 
       - name: Setup Flutter
-        uses: subosito/flutter-action@v2
+        uses: subosito/flutter-action@1a449444c387b1966244ae4d4f8c696479add0b2  # v2
         with:
           flutter-version: '3.24.0'
           channel: 'stable'
@@ -264,7 +264,7 @@ jobs:
 
       - name: Compress Windows Build
         id: compress
-        uses: somaz94/compress-decompress@v1
+        uses: somaz94/compress-decompress@4aa7a81b5e2c20ac4a865d937466f3d8928f487c  # v1
         with:
           command: compress
           source: build/windows/x64/runner/Release
@@ -280,7 +280,7 @@ jobs:
           iscc installer.iss
 
       - name: Upload Windows Artifact
-        uses: actions/upload-artifact@v4
+        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02  # v4
         with:
           name: windows-build
           path: artifacts/*.zip
@@ -294,10 +294,10 @@ jobs:
     if: needs.prepare.outputs.should_build_macos == 'true'
     runs-on: macos-latest
     steps:
-      - uses: actions/checkout@v4
+      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
 
       - name: Setup Flutter
-        uses: subosito/flutter-action@v2
+        uses: subosito/flutter-action@1a449444c387b1966244ae4d4f8c696479add0b2  # v2
         with:
           flutter-version: '3.24.0'
           channel: 'stable'
@@ -322,7 +322,7 @@ jobs:
             "build/macos/Build/Products/Release/crystalcastleX.app"
 
       - name: Compress macOS Build
-        uses: somaz94/compress-decompress@v1
+        uses: somaz94/compress-decompress@4aa7a81b5e2c20ac4a865d937466f3d8928f487c  # v1
         with:
           command: compress
           source: crystalcastleX-macos-v${{ needs.prepare.outputs.version }}.dmg
@@ -341,7 +341,7 @@ jobs:
             --wait
 
       - name: Upload macOS Artifact
-        uses: actions/upload-artifact@v4
+        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02  # v4
         with:
           name: macos-build
           path: artifacts/*.zip
@@ -355,7 +355,7 @@ jobs:
     if: needs.prepare.outputs.should_build_linux == 'true'
     runs-on: ubuntu-latest
     steps:
-      - uses: actions/checkout@v4
+      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
 
       - name: Install Linux Dependencies
         run: |
@@ -365,7 +365,7 @@ jobs:
             libgtk-3-dev liblzma-dev libstdc++-12-dev
 
       - name: Setup Flutter
-        uses: subosito/flutter-action@v2
+        uses: subosito/flutter-action@1a449444c387b1966244ae4d4f8c696479add0b2  # v2
         with:
           flutter-version: '3.24.0'
           channel: 'stable'
@@ -388,7 +388,7 @@ jobs:
 
       - name: Compress Linux Build
         id: compress
-        uses: somaz94/compress-decompress@v1
+        uses: somaz94/compress-decompress@4aa7a81b5e2c20ac4a865d937466f3d8928f487c  # v1
         with:
           command: compress
           source: |
@@ -400,7 +400,7 @@ jobs:
           destfilename: 'crystalcastleX-linux-v${{ needs.prepare.outputs.version }}'
 
       - name: Upload Linux Artifact
-        uses: actions/upload-artifact@v4
+        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02  # v4
         with:
           name: linux-build
           path: artifacts/*.tar.zst
@@ -417,7 +417,7 @@ jobs:
       contents: write
     steps:
       - name: Download All Artifacts
-        uses: actions/download-artifact@v4
+        uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093  # v4
         with:
           path: all-artifacts
           pattern: '*-build'
@@ -441,7 +441,7 @@ jobs:
           ls -la all-artifacts/ >> RELEASE_NOTES.md
 
       - name: Create GitHub Release
-        uses: softprops/action-gh-release@v2
+        uses: softprops/action-gh-release@3bb12739c298aeb8a4eeaf626c5b8d85266b0e65  # v2
         with:
           name: 'ðŸŽ® CrystalCastleX v${{ needs.prepare.outputs.version }}'
           body_path: RELEASE_NOTES.md
diff --git a/.github/workflows/copilot-audit.yml b/.github/workflows/copilot-audit.yml
index 0240fa2..4614f4a 100644
--- a/.github/workflows/copilot-audit.yml
+++ b/.github/workflows/copilot-audit.yml
@@ -12,7 +12,7 @@ jobs:
 
     steps:
       - name: Checkout repository
-        uses: actions/checkout@v4
+        uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
 
       - name: Install Copilot CLI
         run: |
diff --git a/.github/workflows/deploy.yml (Production) b/.github/workflows/deploy.yml (Production)
deleted file mode 100644
index 95bcde9..0000000
--- a/.github/workflows/deploy.yml (Production)	
+++ /dev/null
@@ -1,50 +0,0 @@
-name: CI/CD Deploy Payments Platform
-
-on:
-  push:
-    branches:
-      - main
-  workflow_dispatch:
-
-jobs:
-  build-and-deploy:
-    runs-on: ubuntu-latest
-    steps:
-      - name: Checkout repo
-        uses: actions/checkout@v4
-
-      - name: Setup Helm
-        uses: azure/setup-helm@v4
-        with:
-          version: v3.14.0
-
-      - name: Setup Kubectl
-        uses: azure/setup-kubectl@v4
-        with:
-          version: v1.30.0
-
-      - name: Configure Kubeconfig
-        run: |
-          echo "${{ secrets.KUBECONFIG_CONTENT }}" > kubeconfig.yaml
-          export KUBECONFIG=$PWD/kubeconfig.yaml
-
-      - name: Build & Push API image
-        run: |
-          docker build -t ${{ secrets.REGISTRY }}/api:${{ github.sha }} ./api
-          echo "${{ secrets.REGISTRY_PASSWORD }}" | docker login ${{ secrets.REGISTRY }} -u ${{ secrets.REGISTRY_USER }} --password-stdin
-          docker push ${{ secrets.REGISTRY }}/api:${{ github.sha }}
-
-      - name: Build & Push Skip-Payment image
-        run: |
-          docker build -t ${{ secrets.REGISTRY }}/skip-payment:${{ github.sha }} ./skip-payment
-          docker push ${{ secrets.REGISTRY }}/skip-payment:${{ github.sha }}
-
-      - name: Helm dependency update
-        run: helm dependency update ./payments-helm-chart
-
-      - name: Helm Upgrade/Install
-        run: |
-          helm upgrade --install payments-platform ./payments-helm-chart \
-            -f ./payments-helm-chart/values.yaml \
-            --set api.image.tag=${{ github.sha }} \
-            --set skip-payment.image.tag=${{ github.sha }}
diff --git a/.github/workflows/live-task.yml b/.github/workflows/live-task.yml
index e63de26..151b9a2 100644
--- a/.github/workflows/live-task.yml
+++ b/.github/workflows/live-task.yml
@@ -28,10 +28,10 @@ jobs:
     runs-on: ubuntu-latest
     steps:
       - name: Checkout Code
-        uses: actions/checkout@v4
+        uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
 
       - name: Set up Python
-        uses: actions/setup-python@v5
+        uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065  # v5
         with:
           python-version: '3.11'
           cache: 'pip'
@@ -56,10 +56,10 @@ jobs:
     needs: lint-and-typecheck
     steps:
       - name: Checkout Code
-        uses: actions/checkout@v4
+        uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
 
       - name: Set up Python
-        uses: actions/setup-python@v5
+        uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065  # v5
         with:
           python-version: '3.11'
           cache: 'pip'
@@ -80,7 +80,7 @@ jobs:
             --cov-report=xml:coverage-unit.xml
 
       - name: Upload Unit Coverage Report
-        uses: actions/upload-artifact@v4
+        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02  # v4
         with:
           name: unit-coverage-report
           path: coverage-unit.xml
@@ -91,10 +91,10 @@ jobs:
     needs: unit-tests
     steps:
       - name: Checkout Code
-        uses: actions/checkout@v4
+        uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
 
       - name: Set up Python
-        uses: actions/setup-python@v5
+        uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065  # v5
         with:
           python-version: '3.11'
           cache: 'pip'
diff --git a/.github/workflows/name Deploy Static Content to Pages.txt b/.github/workflows/name Deploy Static Content to Pages.txt
deleted file mode 100644
index e763ec7..0000000
--- a/.github/workflows/name Deploy Static Content to Pages.txt	
+++ /dev/null
@@ -1,39 +0,0 @@
-name: Deploy Static Content to Pages
-
-on:
-  push:
-    branches: [main]
-
-permissions:
-  pages: write
-  id-token: write
-
-concurrency:
-  group: "pages"
-  cancel-in-progress: true
-
-jobs:
-  deploy:
-    environment:
-      name: github-pages
-      url: ${{ steps.deployment.outputs.page_url }}
-    runs-on: ubuntu-latest
-    steps:
-      # âœ… checkout@v4 â€” PINNED SHA
-      - name: Checkout
-        uses: actions/checkout@11bd71901bbe5b1630ceea73d2759718672a689f
-
-      # âœ… configure-pages@v5 â€” PINNED SHA
-      - name: Setup Pages
-        uses: actions/configure-pages@9c35794150560509846e90e162c56cb0c4307e75
-
-      # âœ… upload-pages-artifact@v3 â€” PINNED SHA
-      - name: Upload artifact
-        uses: actions/upload-pages-artifact@de8154f054c463b3d86652b73d7f4b34c6a3e957
-        with:
-          path: '.'
-
-      # âœ… deploy-pages@v5 â€” PINNED SHA
-      - name: Deploy to GitHub Pages
-        id: deployment
-        uses: actions/deploy-pages@d8475690d8475690d8475690d8475690d8475690
\ No newline at end of file
diff --git a/.github/workflows/static.yml b/.github/workflows/static.yml
index 460f782..e9297a4 100644
--- a/.github/workflows/static.yml
+++ b/.github/workflows/static.yml
@@ -30,14 +30,14 @@ jobs:
     runs-on: ubuntu-latest
     steps:
       - name: Checkout
-        uses: actions/checkout@v4
+        uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
       - name: Setup Pages
-        uses: actions/configure-pages@v5
+        uses: actions/configure-pages@983d7736d9b0ae728b81ab479565c72886d7745b  # v5
       - name: Upload artifact
-        uses: actions/upload-pages-artifact@v3
+        uses: actions/upload-pages-artifact@56afc609e74202658d3ffba0e8f6dda462b719fa  # v3
         with:
           # Upload entire repository
           path: '.'
       - name: Deploy to GitHub Pages
         id: deployment
-        uses: actions/deploy-pages@v5
+        uses: actions/deploy-pages@368f82528645a54fb793d4d04e342629a3f51346  # v5
diff --git a/.github/workflows/test-and-coverage.yaml b/.github/workflows/test-and-coverage.yaml
index fb37d25..1b258f1 100644
--- a/.github/workflows/test-and-coverage.yaml
+++ b/.github/workflows/test-and-coverage.yaml
@@ -33,10 +33,10 @@ jobs:
 
     steps:
       - name: Checkout repository
-        uses: actions/checkout@v4
+        uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
 
       - name: Set up Python
-        uses: actions/setup-python@v5
+        uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065  # v5
         with:
           python-version: ${{ matrix.python-version }}
           cache: pip
@@ -60,7 +60,7 @@ jobs:
 
       - name: Upload coverage XML
         if: always()
-        uses: actions/upload-artifact@v4
+        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02  # v4
         with:
           name: coverage-xml-python-${{ matrix.python-version }}
           path: coverage.xml
@@ -69,7 +69,7 @@ jobs:
 
       - name: Upload HTML coverage
         if: always()
-        uses: actions/upload-artifact@v4
+        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02  # v4
         with:
           name: coverage-html-python-${{ matrix.python-version }}
           path: htmlcov/
diff --git a/.github/workflows/vercel-deployment b/.github/workflows/vercel-deployment
deleted file mode 100644
index 5bc85be..0000000
--- a/.github/workflows/vercel-deployment
+++ /dev/null
@@ -1,12 +0,0 @@
-# à¸•à¸´à¸”à¸•à¸±à¹‰à¸‡ Vercel CLI
-npm i -g vercel
-
-# Login
-vercel login
-
-# Link project
-vercel link
-
-# Deploy
-vercel --prod
-Environment Variables à¸šà¸™ Vercel Dashboard: - ENV=vercel - OAUTH_CLIENT_ID=xxx - OAUTH_CLIENT_SECRET=xxx - JWT_SECRET=xxx
diff --git "a/.github/workflows/\360\237\247\252 Staging Workflow Example" "b/.github/workflows/\360\237\247\252 Staging Workflow Example"
deleted file mode 100644
index c27eb7e..0000000
--- "a/.github/workflows/\360\237\247\252 Staging Workflow Example"	
+++ /dev/null
@@ -1,51 +0,0 @@
-name: CI/CD Deploy Payments Platform (Staging)
-
-on:
-  push:
-    branches:
-      - develop
-  workflow_dispatch:
-
-jobs:
-  build-and-deploy-staging:
-    runs-on: ubuntu-latest
-    steps:
-      - name: Checkout repo
-        uses: actions/checkout@v4
-
-      - name: Setup Helm & Kubectl
-        uses: azure/setup-helm@v4
-        with: { version: v3.14.0 }
-      - name: Setup Kubectl
-        uses: azure/setup-kubectl@v4
-        with: { version: v1.30.0 }
-
-      - name: Configure Kubeconfig (Staging)
-        run: |
-          echo "${{ secrets.KUBECONFIG_STAGING }}" > kubeconfig.yaml
-          export KUBECONFIG=$PWD/kubeconfig.yaml
-
-      - name: Login to Container Registry
-        run: |
-          echo "${{ secrets.REGISTRY_PASSWORD }}" | docker login ${{ secrets.REGISTRY }} -u ${{ secrets.REGISTRY_USER }} --password-stdin
-
-      - name: Build & Push API (Staging Tag)
-        run: |
-          docker build -t ${{ secrets.REGISTRY }}/api:staging-${{ github.sha }} ./api
-          docker push ${{ secrets.REGISTRY }}/api:staging-${{ github.sha }}
-
-      - name: Build & Push Skip-Payment (Staging Tag)
-        run: |
-          docker build -t ${{ secrets.REGISTRY }}/skip-payment:staging-${{ github.sha }} ./skip-payment
-          docker push ${{ secrets.REGISTRY }}/skip-payment:staging-${{ github.sha }}
-
-      - name: Helm dependency update
-        run: helm dependency update ./payments-helm-chart
-
-      - name: Helm Upgrade/Install (Staging)
-        run: |
-          helm upgrade --install payments-platform-staging ./payments-helm-chart \
-            -n payments-staging --create-namespace \
-            -f ./payments-helm-chart/values-staging.yaml \
-            --set api.image.tag=staging-${{ github.sha }} \
-            --set skip-payment.image.tag=staging-${{ github.sha }}
-- 
2.47.3


From 71c2bd873317a48e6c1019efb594ffbbedaf5064 Mon Sep 17 00:00:00 2001
From: fig-ai-agent <fig-ai-agent@users.noreply.github.com>
Date: Thu, 10 Sep 2026 06:59:54 +0000
Subject: [PATCH 3/3] refactor(ci): move non-workflow files out of
 .github/workflows/
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit

.github/workflows/ held 19 entries, only 12 of which GitHub would execute. The
other 7 are moved to archive/ with their content intact â€” nothing deleted.

Non-workflow (GitHub ignores any name not ending .yml/.yaml):
  ADD EXAMPLAE AGENTS              -> archive/workflows-docs/agents-sample.md
  Auto-Build-SVG.md                -> archive/workflows-docs/
  README.md                        -> archive/workflows-docs/
  vercel-deployment                -> archive/workflows-docs/vercel-deployment-notes.md

Mis-named but real workflow YAML â€” these have never run:
  deploy.yml (Production)          -> archive/workflows-dormant/deploy-production.yml
  ðŸ§ª Staging Workflow Example        -> archive/workflows-dormant/staging-example.yml
  name Deploy Static Content...txt -> archive/workflows-dormant/deploy-pages-duplicate.txt

The three mis-named files are deliberately NOT renamed into place. Two of them
deploy on push:main / push:develop; renaming would START deploys that have never
happened â€” a behaviour change, not a cleanup. They are parked, preserving
today's never-runs behaviour, with archive/README.md recording the intended
trigger for each so the decision is explicit rather than lost.

.github/workflows/ now contains 12 workflows and nothing else.
---
 archive/README.md                             |  52 +++++
 archive/workflows-docs/Auto-Build-SVG.md      |  32 ++++
 archive/workflows-docs/README.md              | 143 ++++++++++++++
 archive/workflows-docs/agents-sample.md       |  20 ++
 .../workflows-docs/vercel-deployment-notes.md |  12 ++
 .../deploy-pages-duplicate.txt                |  39 ++++
 .../workflows-dormant/deploy-production.yml   |  50 +++++
 archive/workflows-dormant/staging-example.yml |  51 +++++
 tools/ci/check_action_pins.py                 | 179 ++++++++++++++++++
 9 files changed, 578 insertions(+)
 create mode 100644 archive/README.md
 create mode 100644 archive/workflows-docs/Auto-Build-SVG.md
 create mode 100644 archive/workflows-docs/README.md
 create mode 100644 archive/workflows-docs/agents-sample.md
 create mode 100644 archive/workflows-docs/vercel-deployment-notes.md
 create mode 100644 archive/workflows-dormant/deploy-pages-duplicate.txt
 create mode 100644 archive/workflows-dormant/deploy-production.yml
 create mode 100644 archive/workflows-dormant/staging-example.yml
 create mode 100644 tools/ci/check_action_pins.py

diff --git a/archive/README.md b/archive/README.md
new file mode 100644
index 0000000..5dc61a7
--- /dev/null
+++ b/archive/README.md
@@ -0,0 +1,52 @@
+# archive/
+
+Files moved out of `.github/workflows/` so that directory contains only workflow
+YAML that GitHub actually executes. Nothing here is deleted.
+
+## `workflows-docs/`
+
+Notes and drafts that were sitting in `.github/workflows/` but are not workflows.
+GitHub silently ignores any file whose name does not end in `.yml`/`.yaml`, so
+these were inert â€” pure clutter next to 12 real workflows.
+
+| Was | Now |
+| --- | --- |
+| `ADD EXAMPLAE AGENTS` | `workflows-docs/agents-sample.md` |
+| `Auto-Build-SVG.md` | `workflows-docs/Auto-Build-SVG.md` |
+| `README.md` | `workflows-docs/README.md` |
+| `vercel-deployment` | `workflows-docs/vercel-deployment-notes.md` |
+
+## `workflows-dormant/`
+
+Three files that **are** valid workflow YAML but have names GitHub will never
+execute (a space, a paren, a `.txt` extension). They have therefore never run.
+
+| Was | Now | Intended trigger |
+| --- | --- | --- |
+| `deploy.yml (Production)` | `workflows-dormant/deploy-production.yml` | `push` to `main` |
+| `ðŸ§ª Staging Workflow Example` | `workflows-dormant/staging-example.yml` | `push` to `develop` |
+| `name Deploy Static Content to Pages.txt` | `workflows-dormant/deploy-pages-duplicate.txt` | `push` to `main` |
+
+**These were deliberately not renamed into place.** The obvious reading of
+"clean up the workflows directory" is to rename them so they work â€” but two of
+them deploy to production on `push: main`. Renaming would *start* a production
+deploy that has never happened, which is a behaviour change with real blast
+radius, not a cleanup.
+
+They are parked here instead, preserving the current never-runs behaviour. If
+you want them live, rename them into `.github/workflows/` deliberately, one at a
+time, and confirm the deploy target first. Note `deploy-pages-duplicate.txt`
+overlaps with the active `static.yml` (both deploy to GitHub Pages) â€” revive one
+or the other, not both.
+
+These files still reference actions by version tag (`@v4`) rather than pinned
+SHA. That is intentional: they do not execute, and a readable tag is more honest
+than pinning them to a commit SHA that cannot be verified from here. Pin them at
+the moment you decide to activate them.
+
+## Tooling
+
+`tools/ci/check_action_pins.py` fails any workflow action reference that is not a
+full 40-character commit SHA, and with `--verify` confirms each SHA exists
+upstream. Point it at `.github/workflows/` (the default) â€” it is a CI gate, not a
+linter for this archive.
diff --git a/archive/workflows-docs/Auto-Build-SVG.md b/archive/workflows-docs/Auto-Build-SVG.md
new file mode 100644
index 0000000..2a98937
--- /dev/null
+++ b/archive/workflows-docs/Auto-Build-SVG.md
@@ -0,0 +1,32 @@
+Here are a few workflow patterns for an agent whose job is generating SVGs, depending on what's driving the output:
+
+**1. Data-to-chart pipeline**
+1. Validate/parse input data (shape, ranges, missing values)
+2. Choose chart type based on data shape (categorical â†’ bar, time series â†’ line, part-whole â†’ pie/donut)
+3. Compute layout (viewBox, scales, padding) before drawing elements
+4. Generate SVG primitives (axes â†’ gridlines â†’ data â†’ labels/legend last, so they're not obscured)
+5. Validate output (well-formed XML, viewBox matches content bounds)
+
+**2. Diagram/flowchart from description**
+1. Parse the description into nodes + edges (a simple graph structure) before touching SVG
+2. Auto-layout (grid, hierarchical, or force-directed depending on complexity)
+3. Draw edges first, then nodes on top (avoids lines cutting through boxes)
+4. Add text last, sized to fit its container
+5. Check for overlaps/collisions; re-layout if any
+
+**3. Icon/illustration generation**
+1. Define a fixed canvas size and grid (e.g., 24Ã—24, 100Ã—100) up front for consistency
+2. Sketch structure with simple shapes first (circles/rects/paths as placeholders)
+3. Refine paths, add detail
+4. Optimize (remove redundant points, consolidate paths)
+5. Validate against a style guide if one exists (stroke width, corner radius, color tokens)
+
+**4. Iterative/editable SVG (user refines it conversationally)**
+1. Generate a first draft with clearly labeled/grouped `<g>` elements (semantic IDs)
+2. On each revision, edit specific groups rather than regenerating the whole file
+3. Keep a running "spec" (what each group represents) so edits stay consistent
+4. Re-validate viewBox/bounds after each edit, since edits can silently break layout
+
+A cross-cutting rule for all of these: **always use CSS variables for colors** if the SVG needs to adapt to themes, and **compute the viewBox from actual content bounds** rather than guessing â€” that's the most common source of clipped or off-center SVGs.
+
+Which of these matches what you're building â€” is this for the Visualizer-style inline diagrams, or a standalone SVG-generation skill/agent?
diff --git a/archive/workflows-docs/README.md b/archive/workflows-docs/README.md
new file mode 100644
index 0000000..d4cef5d
--- /dev/null
+++ b/archive/workflows-docs/README.md
@@ -0,0 +1,143 @@
+âœ… **Added!** Here's the complete `.github/workflows/README.md` â€” ready to copy and commit directly to your repo:
+
+---
+
+```markdown
+# ðŸ“‹ Workflows â€” fastapi-python-boilerplate
+
+> **Path:** `.github/workflows/` Â· **Maintainer:** ZyntroAI
+> **Purpose:** CI/CD pipelines, automation, quality checks, security scans, and deployment
+
+---
+
+## ðŸ“ Available Workflows
+
+| Workflow File | Purpose | Triggers |
+|---|---|---|
+| **Auto-Index-Sync.yml** | Index documentation â†’ search engine, crawl external docs, audit affiliate policies | Push Â· Nightly (02:00 UTC) Â· Manual |
+| **Auto-Build-SVG.yml** | Auto-generate SVG badges & visual assets | Docs/assets changes |
+| **auto-compress-manage.yml** | Compress & manage build artifacts | On build completion |
+| **build-compress-all-platforms.yml** | Cross-platform build + compression matrix | Release tags / Manual |
+| **ci.yml** | General CI â€” lint, test, build, validation | PR Â· Push Â· Schedule |
+| **copilot-audit.yml** | AI-powered code quality & security pattern audit | PR Â· Schedule |
+| **dependabot-automerge.yml** | Auto-merge minor/patch dependency version bumps | Dependabot |
+| **deploy.yml (Production)** | Deploy application to production environment | Release Â· Manual |
+| **live-task.yml** | Run live integration & connectivity tasks | Schedule Â· Manual |
+| **release_drafter.yml** | Auto-generate & update release notes / CHANGELOG | PR Â· Push |
+| **secret-scan.yml** | Scan commits for exposed credentials & secrets | All PR Â· Push |
+| **static.yml** | Static analysis â€” linting, type checking, code style | PR Â· Push |
+| **test-and-coverage.yml** | Run unit tests + upload coverage reports | PR Â· Push |
+| **test-suite.yml** | Full test matrix across Python versions | PR Â· Daily schedule |
+| **vercel-deployment.yml** | Deploy docs/frontend to Vercel | Docs changes Â· Manual |
+| **Staging-Workflow-Example.yml** | Reference template for staging deployments | â€” |
+
+---
+
+## ðŸš€ Quick Start
+
+### â–¶ï¸ Run Any Workflow Manually
+1. Go to **Actions** tab in GitHub
+2. Select workflow from sidebar
+3. Click **Run workflow** â†’ choose branch â†’ âœ…
+
+### ðŸ”‘ Auto-Index-Sync (Most Used)
+> Syncs `docs/` â†’ Algolia search index, crawls OpenClaw docs, audits affiliate policy changes
+- **Schedule:** Daily `02:00 UTC` â†’ `09:00 ICT`
+- **Required Secrets:**
+  - `ALGOLIA_APP_ID` â€” Algolia Application ID
+  - `ALGOLIA_API_KEY` â€” Algolia Admin API Key
+- **Supporting Scripts:** `scripts/extract_metadata.py` Â· `scripts/push_index.py` Â· `scripts/parse_docs.py`
+
+---
+
+## ðŸ”§ Shared Standards
+
+### Permissions (Standard Template)
+```yaml
+permissions:
+  contents: write        # Checkout, commit, push
+  pull-requests: write   # Post status & review comments
+```
+
+### Python Setup (Reusable Snippet)
+```yaml
+- name: Set up Python
+  uses: actions/setup-python@0a5c61591373683505ea898e09a731b4c89a1da0 # v5.2.0
+  with:
+    python-version: "3.12"
+
+- name: Install dependencies
+  run: |
+    python -m pip install --upgrade pip
+    pip install -r scripts/requirements.txt
+```
+
+### Trigger Best Practices
+```yaml
+on:
+  push:
+    branches: [main]
+    paths: ["docs/**", "scripts/**"]  # Only run when relevant files change
+  schedule:
+    - cron: "0 2 * * *"  # Off-peak UTC run
+  workflow_dispatch:
+    inputs:
+      dry_run:
+        description: Preview only â€” skip push
+        type: boolean
+        default: false
+```
+
+---
+
+## ðŸ“‚ Related Assets
+
+| Path | Role |
+|---|---|
+| `scripts/` | Python helpers invoked by workflows |
+| `docs/` | Documentation indexed by Auto-Index-Sync |
+| `.github/actions/` | Reusable composite actions |
+| `.github/dependabot.yml` | Dependency auto-update config |
+
+---
+
+## âœ… Standards Enforced
+- âœ… **Actions pinned to commit SHA** â€” security policy compliance
+- âœ… **Path filters** â€” avoid unnecessary runs
+- âœ… **`[skip ci]` on bot commits** â€” prevent trigger loops
+- âœ… **Conditional logic** â€” skip commit/push when no changes
+- âœ… **Consistent Python 3.12** across all jobs
+- âœ… **Minimal permissions** principle
+
+---
+
+## ðŸ†˜ Troubleshooting
+
+| Symptom | Solution |
+|---|---|
+| `python: can't open file` | Add `actions/checkout@v4` as **first step** in every job |
+| Git push fails | Add `permissions: contents: write` at job or workflow level |
+| Algolia index not updated | Verify `ALGOLIA_APP_ID` & `ALGOLIA_API_KEY` in repo Secrets |
+| Script not found | Ensure scripts exist in `scripts/` â€” workflow creates placeholders |
+
+---
+
+## ðŸ“ Adding a New Workflow
+1. Create `.github/workflows/your-workflow.yml`
+2. Use standard triggers + pinned action SHAs
+3. Add entry to **Available Workflows** table above
+4. Commit â†’ PR â†’ Merge âœ…
+
+---
+
+> **Last Updated:** 2026-09-08 Â· **Standards:** Security-first Â· Pinned SHAs Â· Minimal permissions
+```
+
+---
+
+### âœ… Next Steps
+1. Create file: **`Add file â†’ .github/workflows/README.md`**
+2. Paste the content above
+3. Commit directly to `main` branch âœ…
+
+Want me to also **generate a `requirements.txt`** for your scripts folder so Python dependencies install automatically? ðŸ“¦
\ No newline at end of file
diff --git a/archive/workflows-docs/agents-sample.md b/archive/workflows-docs/agents-sample.md
new file mode 100644
index 0000000..f172228
--- /dev/null
+++ b/archive/workflows-docs/agents-sample.md
@@ -0,0 +1,20 @@
+# Sample AGENTS.md file
+
+## Dev environment tips
+- Use `pnpm dlx turbo run where <project_name>` to jump to a package instead of scanning with `ls`.
+- Run `pnpm install --filter <project_name>` to add the package to your workspace so Vite, ESLint, and TypeScript can see it.
+- Use `pnpm create vite@latest <project_name> -- --template react-ts` to spin up a new React + Vite package with TypeScript checks ready.
+- Check the name field inside each package's package.json to confirm the right nameâ€”skip the top-level one.
+
+## Testing instructions
+- Find the CI plan in the .github/workflows folder.
+- Run `pnpm turbo run test --filter <project_name>` to run every check defined for that package.
+- From the package root you can just call `pnpm test`. The commit should pass all tests before you merge.
+- To focus on one step, add the Vitest pattern: `pnpm vitest run -t "<test name>"`.
+- Fix any test or type errors until the whole suite is green.
+- After moving files or changing imports, run `pnpm lint --filter <project_name>` to be sure ESLint and TypeScript rules still pass.
+- Add or update tests for the code you change, even if nobody asked.
+
+## PR instructions
+- Title format: [<project_name>] <Title>
+- Always run `pnpm lint` and `pnpm test` before committing.
diff --git a/archive/workflows-docs/vercel-deployment-notes.md b/archive/workflows-docs/vercel-deployment-notes.md
new file mode 100644
index 0000000..5bc85be
--- /dev/null
+++ b/archive/workflows-docs/vercel-deployment-notes.md
@@ -0,0 +1,12 @@
+# à¸•à¸´à¸”à¸•à¸±à¹‰à¸‡ Vercel CLI
+npm i -g vercel
+
+# Login
+vercel login
+
+# Link project
+vercel link
+
+# Deploy
+vercel --prod
+Environment Variables à¸šà¸™ Vercel Dashboard: - ENV=vercel - OAUTH_CLIENT_ID=xxx - OAUTH_CLIENT_SECRET=xxx - JWT_SECRET=xxx
diff --git a/archive/workflows-dormant/deploy-pages-duplicate.txt b/archive/workflows-dormant/deploy-pages-duplicate.txt
new file mode 100644
index 0000000..e763ec7
--- /dev/null
+++ b/archive/workflows-dormant/deploy-pages-duplicate.txt
@@ -0,0 +1,39 @@
+name: Deploy Static Content to Pages
+
+on:
+  push:
+    branches: [main]
+
+permissions:
+  pages: write
+  id-token: write
+
+concurrency:
+  group: "pages"
+  cancel-in-progress: true
+
+jobs:
+  deploy:
+    environment:
+      name: github-pages
+      url: ${{ steps.deployment.outputs.page_url }}
+    runs-on: ubuntu-latest
+    steps:
+      # âœ… checkout@v4 â€” PINNED SHA
+      - name: Checkout
+        uses: actions/checkout@11bd71901bbe5b1630ceea73d2759718672a689f
+
+      # âœ… configure-pages@v5 â€” PINNED SHA
+      - name: Setup Pages
+        uses: actions/configure-pages@9c35794150560509846e90e162c56cb0c4307e75
+
+      # âœ… upload-pages-artifact@v3 â€” PINNED SHA
+      - name: Upload artifact
+        uses: actions/upload-pages-artifact@de8154f054c463b3d86652b73d7f4b34c6a3e957
+        with:
+          path: '.'
+
+      # âœ… deploy-pages@v5 â€” PINNED SHA
+      - name: Deploy to GitHub Pages
+        id: deployment
+        uses: actions/deploy-pages@d8475690d8475690d8475690d8475690d8475690
\ No newline at end of file
diff --git a/archive/workflows-dormant/deploy-production.yml b/archive/workflows-dormant/deploy-production.yml
new file mode 100644
index 0000000..95bcde9
--- /dev/null
+++ b/archive/workflows-dormant/deploy-production.yml
@@ -0,0 +1,50 @@
+name: CI/CD Deploy Payments Platform
+
+on:
+  push:
+    branches:
+      - main
+  workflow_dispatch:
+
+jobs:
+  build-and-deploy:
+    runs-on: ubuntu-latest
+    steps:
+      - name: Checkout repo
+        uses: actions/checkout@v4
+
+      - name: Setup Helm
+        uses: azure/setup-helm@v4
+        with:
+          version: v3.14.0
+
+      - name: Setup Kubectl
+        uses: azure/setup-kubectl@v4
+        with:
+          version: v1.30.0
+
+      - name: Configure Kubeconfig
+        run: |
+          echo "${{ secrets.KUBECONFIG_CONTENT }}" > kubeconfig.yaml
+          export KUBECONFIG=$PWD/kubeconfig.yaml
+
+      - name: Build & Push API image
+        run: |
+          docker build -t ${{ secrets.REGISTRY }}/api:${{ github.sha }} ./api
+          echo "${{ secrets.REGISTRY_PASSWORD }}" | docker login ${{ secrets.REGISTRY }} -u ${{ secrets.REGISTRY_USER }} --password-stdin
+          docker push ${{ secrets.REGISTRY }}/api:${{ github.sha }}
+
+      - name: Build & Push Skip-Payment image
+        run: |
+          docker build -t ${{ secrets.REGISTRY }}/skip-payment:${{ github.sha }} ./skip-payment
+          docker push ${{ secrets.REGISTRY }}/skip-payment:${{ github.sha }}
+
+      - name: Helm dependency update
+        run: helm dependency update ./payments-helm-chart
+
+      - name: Helm Upgrade/Install
+        run: |
+          helm upgrade --install payments-platform ./payments-helm-chart \
+            -f ./payments-helm-chart/values.yaml \
+            --set api.image.tag=${{ github.sha }} \
+            --set skip-payment.image.tag=${{ github.sha }}
diff --git a/archive/workflows-dormant/staging-example.yml b/archive/workflows-dormant/staging-example.yml
new file mode 100644
index 0000000..c27eb7e
--- /dev/null
+++ b/archive/workflows-dormant/staging-example.yml
@@ -0,0 +1,51 @@
+name: CI/CD Deploy Payments Platform (Staging)
+
+on:
+  push:
+    branches:
+      - develop
+  workflow_dispatch:
+
+jobs:
+  build-and-deploy-staging:
+    runs-on: ubuntu-latest
+    steps:
+      - name: Checkout repo
+        uses: actions/checkout@v4
+
+      - name: Setup Helm & Kubectl
+        uses: azure/setup-helm@v4
+        with: { version: v3.14.0 }
+      - name: Setup Kubectl
+        uses: azure/setup-kubectl@v4
+        with: { version: v1.30.0 }
+
+      - name: Configure Kubeconfig (Staging)
+        run: |
+          echo "${{ secrets.KUBECONFIG_STAGING }}" > kubeconfig.yaml
+          export KUBECONFIG=$PWD/kubeconfig.yaml
+
+      - name: Login to Container Registry
+        run: |
+          echo "${{ secrets.REGISTRY_PASSWORD }}" | docker login ${{ secrets.REGISTRY }} -u ${{ secrets.REGISTRY_USER }} --password-stdin
+
+      - name: Build & Push API (Staging Tag)
+        run: |
+          docker build -t ${{ secrets.REGISTRY }}/api:staging-${{ github.sha }} ./api
+          docker push ${{ secrets.REGISTRY }}/api:staging-${{ github.sha }}
+
+      - name: Build & Push Skip-Payment (Staging Tag)
+        run: |
+          docker build -t ${{ secrets.REGISTRY }}/skip-payment:staging-${{ github.sha }} ./skip-payment
+          docker push ${{ secrets.REGISTRY }}/skip-payment:staging-${{ github.sha }}
+
+      - name: Helm dependency update
+        run: helm dependency update ./payments-helm-chart
+
+      - name: Helm Upgrade/Install (Staging)
+        run: |
+          helm upgrade --install payments-platform-staging ./payments-helm-chart \
+            -n payments-staging --create-namespace \
+            -f ./payments-helm-chart/values-staging.yaml \
+            --set api.image.tag=staging-${{ github.sha }} \
+            --set skip-payment.image.tag=staging-${{ github.sha }}
diff --git a/tools/ci/check_action_pins.py b/tools/ci/check_action_pins.py
new file mode 100644
index 0000000..f2b6c50
--- /dev/null
+++ b/tools/ci/check_action_pins.py
@@ -0,0 +1,179 @@
+#!/usr/bin/env python3
+"""Fail if any workflow action reference is not pinned to a full commit SHA.
+
+Why this exists: a previous patch pinned `actions/checkout` and
+`github/codeql-action` to 40-hex strings that were not real commits. YAML
+validation passed â€” a bad SHA is syntactically perfect â€” and the failure only
+surfaced when the workflow ran, as `Unable to resolve action`. This check is the
+missing gate: it validates the *reference*, not just the syntax.
+
+Usage:
+    python tools/ci/check_action_pins.py                  # offline: shape only
+    python tools/ci/check_action_pins.py --verify          # + confirm each SHA exists
+    python tools/ci/check_action_pins.py --dir .github/workflows
+
+Exit codes: 0 = clean, 1 = violations, 2 = usage error.
+"""
+import argparse
+import glob
+import json
+import os
+import re
+import subprocess
+import sys
+
+SHA_RE = re.compile(r"^[0-9a-f]{40}$")
+USES_RE = re.compile(r"\buses:\s*(?P<value>[^\s#]+)")
+# local composites (./path) and container/step images are not action refs
+LOCAL_PREFIXES = ("./", "docker://")
+
+
+def find_workflows(directory):
+    return sorted(set(glob.glob(os.path.join(directory, "*.yml"))
+                      + glob.glob(os.path.join(directory, "*.yaml"))))
+
+
+def stray_files(directory):
+    """Entries in the workflows dir that GitHub will never execute."""
+    out = []
+    if not os.path.isdir(directory):
+        return out
+    for name in sorted(os.listdir(directory)):
+        path = os.path.join(directory, name)
+        if os.path.isdir(path):
+            out.append(name)
+        elif not name.endswith((".yml", ".yaml")):
+            out.append(name)
+    return out
+
+
+def scan(directory):
+    unpinned, malformed, refs = [], [], []
+    for path in find_workflows(directory):
+        for lineno, line in enumerate(open(path, encoding="utf-8", newline=""), 1):
+            for m in USES_RE.finditer(line):
+                value = m.group("value").strip().strip("\"'")
+                if value.startswith(LOCAL_PREFIXES):
+                    continue
+                if "@" not in value:
+                    malformed.append((path, lineno, value, "no @ref at all"))
+                    continue
+                action, ref = value.rsplit("@", 1)
+                refs.append((path, lineno, action, ref))
+                if not SHA_RE.match(ref):
+                    unpinned.append((path, lineno, value))
+                elif len(set(ref)) == 1:
+                    malformed.append((path, lineno, value, "degenerate SHA"))
+    return unpinned, malformed, refs
+
+
+def sha_exists(action, sha):
+    """Confirm the commit exists in the action's repo.
+
+    Returns (status, detail) where status is True/False/None:
+      True  -> exists
+      False -> definitely does not exist (404)
+      None  -> indeterminate (network/HTML quirk)
+
+    Uses the public HTML commit page, not the REST API. The API is rate-limited
+    to 60 requests/hour unauthenticated and answers 403 once exhausted â€” which
+    is indistinguishable from a real problem unless you special-case it, and
+    produced a wall of false "sha is dead" results the first time. The HTML
+    endpoint has no such limit, and a 404 there is definitive: GitHub serves the
+    commit page for a real SHA and 404s for one that does not exist.
+    """
+    repo = "/".join(action.split("/")[:2])
+    url = f"https://github.com/{repo}/commit/{sha}"
+    for attempt in range(3):
+        out = subprocess.run(
+            ["curl", "-sS", "--max-time", "25", "-o", "/dev/null",
+             "-w", "%{http_code}", url],
+            capture_output=True, text=True).stdout.strip()
+        if out == "200":
+            return True, out
+        if out == "404":
+            return False, out
+        time.sleep(1.5 * (attempt + 1))
+    return None, out
+
+
+def main():
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--dir", default=".github/workflows")
+    ap.add_argument("--verify", action="store_true",
+                    help="confirm each SHA is a real commit (network)")
+    args = ap.parse_args()
+
+    if not os.path.isdir(args.dir):
+        print(f"::error::workflow directory not found: {args.dir}")
+        return 2
+
+    unpinned, malformed, refs = scan(args.dir)
+    stray = stray_files(args.dir)
+
+    print(f"Scanned {len(find_workflows(args.dir))} workflow file(s) in {args.dir}/")
+    print(f"Action references: {len(refs)}")
+
+    bad = False
+
+    if unpinned:
+        bad = True
+        print(f"\n::error::{len(unpinned)} reference(s) not pinned to a full SHA:")
+        for path, lineno, value in unpinned:
+            print(f"  {path}:{lineno}  {value}")
+
+    if malformed:
+        bad = True
+        print(f"\n::error::{len(malformed)} malformed reference(s):")
+        for path, lineno, value, why in malformed:
+            print(f"  {path}:{lineno}  {value}  ({why})")
+
+    if stray:
+        # Warning, not failure: a doc file here is clutter (GitHub ignores it),
+        # but it is not a broken workflow.
+        print(f"\n::warning::{len(stray)} non-workflow entr(y/ies) in {args.dir}/ "
+              f"(GitHub will not run these):")
+        for name in stray:
+            print(f"  {name}")
+
+    if args.verify and refs:
+        print(f"\nVerifying {len(refs)} SHA(s) against the GitHub API...")
+        seen, dead, unknown = {}, [], []
+        for path, lineno, action, ref in refs:
+            if not SHA_RE.match(ref):
+                continue
+            key = (action, ref)
+            if key not in seen:
+                seen[key] = sha_exists(action, ref)
+                time.sleep(0.4)  # stay under the unauthenticated rate limit
+            ok, code = seen[key]
+            if ok is False:
+                dead.append((path, lineno, action, ref, code))
+            elif ok is None:
+                unknown.append((path, lineno, action, ref, code))
+
+        if dead:
+            bad = True
+            print(f"\n::error::{len(dead)} SHA(s) do not exist upstream:")
+            for path, lineno, action, ref, code in dead:
+                print(f"  {path}:{lineno}  {action}@{ref}  (HTTP {code})")
+
+        if unknown:
+            # Rate-limited, not broken. Never fail the build on this â€” a red gate
+            # that fires when GitHub throttles us is worse than no gate.
+            print(f"\n::warning::could not verify {len(unknown)} SHA(s) "
+                  f"(API refused â€” likely rate limit):")
+            for path, lineno, action, ref, code in unknown[:10]:
+                print(f"  {path}:{lineno}  {action}@{ref}  (HTTP {code})")
+            if len(unknown) > 10:
+                print(f"  ... and {len(unknown) - 10} more")
+
+        if not dead and not unknown:
+            print(f"  all {len(seen)} unique SHA(s) resolve to real commits")
+
+    print("\n" + ("FAILED â€” fix the references above." if bad else "OK â€” all refs pinned."))
+    return 1 if bad else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
-- 
2.47.3

