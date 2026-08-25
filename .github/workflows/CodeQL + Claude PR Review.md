CodeQL + Claude PR Review
// CodeQL + Claude PR Review

.github/
└── workflows/
└── security-review.yml
├── codeql
│ ├── actions
│ ├── javascript-typescript
│ └── python
│
└── claude-review
└── Claude Inline Review

name: Security & AI PR Review

on:
push:
branches:
- main
pull_request:
branches:
- main
types:
- opened
- synchronize
- reopened
schedule:
- cron: "21 17 * * 0"
workflow_dispatch:

permissions:
contents: read
actions: read
packages: read
security-events: write
pull-requests: write
issues: write

============================================================
CodeQL Security Analysis
============================================================

jobs:
codeql:
name: CodeQL ( {{ (matrix.language == 'swift' && 'macos-latest') || 'ubuntu-latest' }}

strategy:
fail-fast: false
matrix:
include:
- language: actions
build-mode: none

- language: javascript-typescript
build-mode: none

- language: python
build-mode: none

steps:
- name: Checkout repository
uses: actions/checkout@v5
with:
fetch-depth: 0

- name: Initialize CodeQL
uses: github/codeql-action/init@v4
with:
languages:  {{ matrix.build-mode }}

# Uncomment to enable broader CodeQL coverage.
# queries: security-extended,security-and-quality

- name: Run manual build
if: matrix.build-mode == 'manual'
shell: bash
run: |
set -euo pipefail

echo "Manual CodeQL build is required."
echo "Replace this section with the project's build commands."

# Example:
# make bootstrap
# make build

exit 1

- name: Perform CodeQL Analysis
uses: github/codeql-action/analyze@v4
with:
category: "/language:$`{{ matrix.language }}"

============================================================
Claude AI Pull Request Review
============================================================

claude-review:
name: Claude Inline Review
runs-on: ubuntu-latest

# Claude review only makes sense for pull requests.
if: github.event_name == 'pull_request'

steps:
- name: Checkout repository
uses: actions/checkout@v5
with:
fetch-depth: 0

- name: Claude Code Review
uses: anthropics/claude-code-action@v1
with:
anthropic_api_key: `${{ secrets.ANTHROPIC_API_KEY }}

prompt: |
Review this pull request.

Focus on:

1. Correctness
2. Bugs
3. Security
4. Authentication and authorization
5. Performance
6. Error handling
7. Maintainability
8. Tests

Review only changes introduced by this pull request.

Post findings as INLINE comments on the exact
changed lines whenever possible.

Do not post generic comments when an inline
comment can be used.

For small, safe fixes, provide a GitHub
suggestion block.

Do not report:

- Style-only nitpicks
- Existing issues unrelated to this PR
- Issues already covered by CI or linter
- Low-confidence findings
- Duplicate findings

Prioritize findings by severity.

If no significant issue exists, leave a short
review summary.

claude_args: |
--allowedTools "mcp__github_inline_comment__create_inline_comment,Bash(gh pr diff:),Bash(gh pr view:),Bash(gh pr comment:*)"

สิ่งที่เปลี่ยน

1. รวมเป็นไฟล์เดียว

.github/workflows/security-review.yml

มี workflow เดียว:

name: Security & AI PR Review

แล้วแยกภายในเป็น:

jobs:
codeql:
claude-review:

2. CodeQL รองรับ repository ของคุณ

• language: actions
build-mode: none

• language: javascript-typescript
build-mode: none

• language: python
build-mode: none

จึงครอบคลุม:

GitHub Actions
↓
JavaScript / TypeScript
↓
Python / FastAPI

3. Claude จะทำเฉพาะ Pull Request

if: github.event_name == 'pull_request'

ดังนั้น push และ schedule จะไม่เรียก Claude API โดยไม่จำเป็น ซึ่งช่วยประหยัด API usage ได้พอสมควร มนุษย์ยังต้องเสียเงินให้ AI ตรวจโค้ดที่ AI เขียนเองต่อไปอีกที เป็นระบบนิเวศที่งดงามมาก

4. CodeQL ทำงานได้ทั้ง PR, push และ scheduled scan

Pull Request
│
├── CodeQL
│
└── Claude Review

Push → main
│
└── CodeQL

Sunday 17:21 UTC
│
└── CodeQL

5. Permission รวมไว้ระดับ workflow

permissions:
contents: read
actions: read
packages: read
security-events: write
pull-requests: write
issues: write

ทำให้ไม่ต้องประกาศซ้ำในแต่ละ job และยังคงหลัก least privilege เท่าที่ workflow นี้ต้องใช้

GitHub Secrets

ต้องมี:

Settings
└── Secrets and variables
└── Actions
└── ANTHROPIC_API_KEY

ชื่อ secret ต้องตรงกับ:

${{ secrets.ANTHROPIC_API_KEY }}

Recommended workflow architecture

สำหรับ repo ที่มี React/Next.js + FastAPI + GitHub Actions ผมจะจัด security pipeline ต่อไปประมาณนี้:

Pull Request
│
┌───────────┴───────────┐
│ │
CodeQL Claude
│ │
┌─────┼─────┐ AI Inline Review
│ │ │ │
Actions TS/JS Python │
│ │ │ │
└─────┼─────┘ │
│ │
└───────────┬───────────┘
│
CI / Tests
│
Security Gates
│
Merge

จุดสำคัญคือ CodeQL กับ Claude ไม่ควรทำหน้าที่แทนกัน: CodeQL เป็น static security analysis ที่ deterministic กว่า ส่วน Claude เหมาะกับ reasoning เช่น business logic, auth flow, error handling และผลกระทบของ diff. การให้สองตัวตรวจคนละมุมจะมีประโยชน์กว่าการให้ AI สองตัวพูดว่า "LGTM" แข่งกันครับ.
