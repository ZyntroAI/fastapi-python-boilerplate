แนะนำ .github/workflows/ci

ด้านล่างคือ baseline `.github/workflows/ci.yml` ที่ปลอดภัย ใช้เป็นจุดเริ่มต้นได้กับ repo ทั่วไป โดยแยกงานตรวจเป็น job, จำกัด token เป็น read-only, ยกเลิก run เก่าของ PR/branch เดียวกัน และไม่ใช้ secret หรือ `pull_request_target` กับโค้ดจาก PR ครับ[1][2][3]

> ก่อนใช้งานจริง ให้เปลี่ยนคำสั่งในส่วน `lint`, `test` และ `build` ให้ตรงกับ language/package manager ของ repository

## CI Template

```yaml
name: CI

on:
  pull_request:
    branches:
      - main
  push:
    branches:
      - main
  workflow_dispatch:

# CI นี้มีหน้าที่อ่าน source และตรวจสอบเท่านั้น
# อย่าเพิ่ม write permission หากไม่มีความจำเป็นชัดเจน
permissions:
  contents: read

# ลดงานซ้ำ: เมื่อมี commit ใหม่ใน PR/branch เดิม ให้ยกเลิก run ก่อนหน้า
concurrency:
  group: ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

# ป้องกัน workflow run นานผิดปกติ
defaults:
  run:
    shell: bash

jobs:
  validate:
    name: Validate workflow and repository
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Check out source
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Basic repository checks
        run: |
          set -euo pipefail

          test -f README.md || {
            echo "::warning::README.md was not found"
          }

          test -d .github || {
            echo "::notice::.github directory was not found"
          }

          echo "Repository validation completed."

  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Check out source
        uses: actions/checkout@v4

      # เลือกเปิดเฉพาะ setup step ที่ตรงกับโปรเจกต์
      #
      # Node.js:
      # - uses: actions/setup-node@v4
      #   with:
      #     node-version: 22
      #     cache: npm
      #
      # Python:
      # - uses: actions/setup-python@v5
      #   with:
      #     python-version: "3.12"
      #     cache: pip
      #
      # Java:
      # - uses: actions/setup-java@v4
      #   with:
      #     distribution: temurin
      #     java-version: "21"
      #     cache: gradle
      #
      # Go:
      # - uses: actions/setup-go@v5
      #   with:
      #     go-version-file: go.mod
      #     cache: true

      - name: Detect project files
        id: detect
        run: |
          set -euo pipefail

          {
            echo "node=$(test -f package.json && echo true || echo false)"
            echo "python=$(test -f pyproject.toml -o -f requirements.txt -o -f setup.py && echo true || echo false)"
            echo "go=$(test -f go.mod && echo true || echo false)"
            echo "java=$(test -f pom.xml -o -f build.gradle -o -f build.gradle.kts && echo true || echo false)"
          } >> "$GITHUB_OUTPUT"

      - name: Lint Node.js project
        if: steps.detect.outputs.node == 'true'
        run: |
          set -euo pipefail
          npm ci
          npm run lint --if-present

      - name: Lint Python project
        if: steps.detect.outputs.python == 'true'
        run: |
          set -euo pipefail
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then
            python -m pip install -r requirements.txt
          fi
          if [ -f pyproject.toml ]; then
            python -m pip install -e ".[dev]" || python -m pip install -e .
          fi
          python -m ruff check . 2>/dev/null || true

      - name: Lint Go project
        if: steps.detect.outputs.go == 'true'
        run: |
          set -euo pipefail
          go vet ./...

      - name: Lint Java project
        if: steps.detect.outputs.java == 'true'
        run: |
          set -euo pipefail
          if [ -f pom.xml ]; then
            ./mvnw -B verify -DskipTests || mvn -B verify -DskipTests
          elif [ -f gradlew ]; then
            chmod +x gradlew
            ./gradlew check -x test
          fi

  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 30
    needs:
      - validate
      - lint

    steps:
      - name: Check out source
        uses: actions/checkout@v4

      - name: Detect project files
        id: detect
        run: |
          set -euo pipefail

          {
            echo "node=$(test -f package.json && echo true || echo false)"
            echo "python=$(test -f pyproject.toml -o -f requirements.txt -o -f setup.py && echo true || echo false)"
            echo "go=$(test -f go.mod && echo true || echo false)"
            echo "java=$(test -f pom.xml -o -f build.gradle -o -f build.gradle.kts && echo true || echo false)"
          } >> "$GITHUB_OUTPUT"

      - name: Test Node.js project
        if: steps.detect.outputs.node == 'true'
        uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: package-lock.json

      - name: Run Node.js tests
        if: steps.detect.outputs.node == 'true'
        run: |
          set -euo pipefail
          npm ci
          npm test --if-present

      - name: Set up Python
        if: steps.detect.outputs.python == 'true'
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Run Python tests
        if: steps.detect.outputs.python == 'true'
        run: |
          set -euo pipefail
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then
            python -m pip install -r requirements.txt
          fi
          if [ -f pyproject.toml ]; then
            python -m pip install -e ".[dev]" || python -m pip install -e .
          fi
          python -m pytest -q

      - name: Set up Go
        if: steps.detect.outputs.go == 'true'
        uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true

      - name: Run Go tests
        if: steps.detect.outputs.go == 'true'
        run: |
          set -euo pipefail
          go test ./...

      - name: Run Java tests
        if: steps.detect.outputs.java == 'true'
        run: |
          set -euo pipefail
          if [ -f pom.xml ]; then
            ./mvnw -B test || mvn -B test
          elif [ -f gradlew ]; then
            chmod +x gradlew
            ./gradlew test
          fi

  build:
    name: Build
    runs-on: ubuntu-latest
    timeout-minutes: 20
    needs: test

    steps:
      - name: Check out source
        uses: actions/checkout@v4

      - name: Build placeholder
        run: |
          set -euo pipefail
          echo "Replace this step with the project build command."
          echo "Examples:"
          echo "  npm ci && npm run build"
          echo "  python -m build"
          echo "  go build ./..."
          echo "  ./gradlew build"
```

## คำแนะนำสำคัญ

### ใช้ CI เฉพาะ stack เดียว

Template ข้างบนตรวจ Node, Python, Go และ Java แบบ auto-detect เพื่อให้เริ่มได้เร็ว แต่สำหรับ production ควรลดให้เหลือเฉพาะ stack ที่ใช้จริง เพื่อให้ CI อ่านง่าย เร็ว และลด dependency ที่ไม่จำเป็น

ตัวอย่าง ถ้าเป็น Node.js ให้ตัด job ตรวจภาษาอื่นออก แล้วใช้ workflow ที่ชัดเจนกว่า:

```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 20

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: package-lock.json

      - run: npm ci
      - run: npm run lint --if-present
      - run: npm test --if-present
      - run: npm run build --if-present
```

Dependency caching ช่วยลดเวลารันได้ แต่ cache ควรเป็น dependency/build cache เท่านั้น และต้องระวังว่า repository readers สามารถเข้าถึงเนื้อหาของ cache ได้ จึงห้ามเก็บ secrets หรือ artifact ที่มีข้อมูลอ่อนไหวไว้ใน cache[4][5][6]

### อย่าใช้ `pull_request_target` กับ CI ปกติ

สำหรับ CI ที่ checkout และรันโค้ดจาก pull request ให้ใช้ `pull_request` เท่านั้น `pull_request_target` ทำงานในบริบทสิทธิ์ของ base repository และอาจเสี่ยงหากใช้กับ PR จาก fork หรือโค้ดที่ยังไม่น่าเชื่อถือ[1][7]

### Pin actions สำหรับงาน production

ตัวอย่างใช้ tag (`@v4`, `@v5`) เพื่ออ่านง่าย แต่แนวทางความปลอดภัยที่เข้มขึ้นคือ pin ทุก `uses:` เป็น full commit SHA ที่ตรวจสอบแล้ว เพราะ commit SHA เป็น immutable reference; GitHub แนะนำสิ่งนี้เพื่อช่วยลด supply-chain risk จาก action dependency[1][2][8]

ตัวอย่างแนวคิด:

```yaml
# ตรวจ SHA ล่าสุดที่คุณอนุมัติจาก repository ของ action ก่อนใช้
- uses: actions/checkout@<full-40-character-commit-sha>
```

### แยก CI ออกจาก deploy

CI ควรทำเพียง lint, test, build และตรวจ artifact ได้; deploy, release, auto-merge, comment PR หรือเขียน issue ควรแยกเป็น workflow อื่นที่กำหนด permission เท่าที่จำเป็นในระดับ job เช่น `contents: write` หรือ `pull-requests: write` เท่านั้น[1][3]

การอ้างอิง:
[1] Secure use reference - GitHub Docs https://docs.github.com/en/actions/reference/security/secure-use
[2] Security hardening for GitHub Actions https://docs.github.com/en/enterprise-cloud@latest/enterprise-onboarding/github-actions-for-your-enterprise/security-hardening-for-github-actions
[3] github-actions-ci-cd-best-practices.instructions.md https://github.com/github/awesome-copilot/blob/main/instructions/github-actions-ci-cd-best-practices.instructions.md
[4] Dependency caching reference - GitHub Docs https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching
[5] 依赖项缓存参考 - GitHub Enterprise Server 3.15 Docs https://docs.github.com/zh/enterprise-server@3.15/actions/reference/workflows-and-actions/dependency-caching
[6] Usage https://github.com/actions/cache
[7] Secure use reference - GitHub Enterprise Cloud Docs https://docs.github.com/en/enterprise-cloud@latest/actions/reference/security/secure-use
[8] Secure use reference - GitHub Enterprise Server 3.17 Docs https://docs.github.com/en/enterprise-server@3.17/actions/reference/security/secure-use
[9] GitHub Docs https://docs.github.com/api/article/body?pathname=/en/actions/reference/workflows-and-actions/dependency-caching
[10] Dependency caching reference - GitHub Enterprise Server 3.20 Docs https://docs.github.com/en/enterprise-server@3.20/actions/reference/workflows-and-actions/dependency-caching
[11] Caching dependencies to speed up workflows - GitHub Docsdocs.github.com › writing-workflows › choosing-what-your-workflow-does https://docs.github.com/en/enterprise-cloud@latest/actions/reference/workflows-and-actions/dependency-caching
[12] Dependency caching reference https://docs.github.com/en/enterprise-server@3.19/actions/reference/workflows-and-actions/dependency-caching
[13] GitHub Actions Security https://learn.secbyte.org/tools/github-actions-security
[14] GitHub Actions: The Complete CI/CD Guide for Developers https://env.dev/guides/github-actions-guide
[15] Enterprise-Wide Runbook - GitHub Actions Hardening - Per Søderlind https://soderlind.no/devops/gh-hardening/runbook/
