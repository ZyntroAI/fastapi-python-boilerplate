สรุปทั้งหมด ขอผลลัพธ์ที่พร้อมเอาไปสร้างเป็นเอกสาร ใน Obsidian Mobile App

# คู่มือจัดการ GitHub Pull Request Data ด้วย CLI

> เอกสารนี้รวบรวม workflow สำหรับดึงข้อมูล Pull Request จาก GitHub, ส่งออกเป็น CSV/JSON, รวมและเชื่อมข้อมูล, ป้องกัน row multiplication และวิเคราะห์ CSV ขนาดใหญ่ด้วย DuckDB บน Terminal  
>  
> ตัวอย่างใช้ repository: `ZyntroAI/Development`  
> เปลี่ยน `OWNER`, `REPO`, `PR_NUMBER` และ path ไฟล์ให้ตรงกับโปรเจกต์ของคุณ

***

## 1. ภาพรวม Workflow

```text
GitHub
  │
  ├─ gh api / gh pr list
  │    ├─ PR metadata
  │    ├─ Reviews
  │    ├─ Inline review comments
  │    └─ Discussion comments
  │
  ├─ JSON / CSV exports
  │
  ├─ csvstack
  │    └─ รวมไฟล์ชนิดเดียวกันแบบต่อแถว
  │
  ├─ csvjoin / DuckDB JOIN
  │    └─ เชื่อมข้อมูลด้วย pr_number
  │
  ├─ Aggregate ก่อน JOIN
  │    └─ ป้องกัน row multiplication
  │
  └─ Export รายงาน
       ├─ CSV
       ├─ Parquet
       └─ Database .duckdb
```

***

## 2. เครื่องมือที่ต้องมี

| เครื่องมือ | หน้าที่หลัก |
|---|---|
| `gh` | GitHub CLI สำหรับ login, ดึง PR, commit, review และ comments |
| `jq` | กรอง/แปลง JSON เป็น CSV หรือ JSON ที่อ่านง่าย |
| `csvkit` | จัดการ CSV ด้วย `csvstack`, `csvjoin`, `csvsql`, `csvcut` |
| DuckDB | Query CSV ขนาดใหญ่ด้วย SQL, aggregate, join และ export |
| `qsv` | เครื่องมือ CSV ความเร็วสูง เหมาะกับไฟล์ใหญ่ |
| Miller (`mlr`) | ทำ data pipeline แบบ streaming สำหรับ CSV/TSV/JSON/JSONL |

### ตรวจสอบว่าติดตั้งแล้ว

```bash
gh --version
jq --version
csvstack --version
duckdb --version
qsv --version
mlr --version
```

### ติดตั้งพื้นฐาน

```bash
# GitHub CLI
brew install gh

# JSON processor
brew install jq

# csvkit
python3 -m pip install --user csvkit

# DuckDB
brew install duckdb

# qsv
brew install qsv

# Miller
brew install miller
```

บน Linux ใช้ package manager ของ distribution หรือ `pipx install csvkit` สำหรับ csvkit

***

## 3. GitHub Authentication

ก่อนเรียก GitHub API หรือ push ต้อง login ก่อน:

```bash
gh auth login
gh auth status
gh auth setup-git
```

### ปัญหาที่พบบ่อย

```text
fatal: could not read Username for 'https://github.com'
```

สาเหตุหลักคือ shell session ไม่มี credential, `gh` ยังไม่ login, ไม่มี `GH_TOKEN`/`GITHUB_TOKEN`, หรือ Git ไม่ได้ตั้ง credential helper

แนวทางแก้:

```bash
gh auth login
gh auth setup-git
git push -u origin fig/your-branch
```

### สำหรับ CI / GitHub Actions

```yaml
- uses: actions/checkout@v4
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    persist-credentials: true

- name: Configure GitHub authentication
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh auth setup-git
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
```

> อย่าแสดง token ใน terminal output, log, source code หรือ commit

***

## 4. ตัวแปรสำหรับใช้งาน

สร้างไฟล์ `env.sh`:

```bash
export OWNER="ZyntroAI"
export REPO="Development"
export REPO_SLUG="$OWNER/$REPO"

export PR_NUMBER=123
export OUTDIR="exports"

mkdir -p "$OUTDIR"
```

โหลดตัวแปร:

```bash
source env.sh
```

***

## 5. ดึงข้อมูล Commit

### ดู commit หนึ่งรายการจาก SHA

```bash
gh api "/repos/$OWNER/$REPO/commits/6648feeb47d73f294bfb8b9de2d016109f71c172"
```

### สรุป commit

```bash
gh api "/repos/$OWNER/$REPO/commits/6648feeb47d73f294bfb8b9de2d016109f71c172" \
  --jq '{
    sha: .sha,
    message: .commit.message,
    author: .commit.author.name,
    date: .commit.author.date,
    files_changed: (.files | length),
    total_additions: ([.files[].additions] | add),
    total_deletions: ([.files[].deletions] | add)
  }'
```

### ดูไฟล์ที่เปลี่ยน

```bash
gh api "/repos/$OWNER/$REPO/commits/6648feeb47d73f294bfb8b9de2d016109f71c172" \
  --jq '.files[] | {
    filename,
    status,
    additions,
    deletions
  }'
```

### ดึง patch

```bash
gh api \
  -H "Accept: application/vnd.github.patch" \
  "/repos/$OWNER/$REPO/commits/6648feeb47d73f294bfb8b9de2d016109f71c172" \
  > "$OUTDIR/commit.patch"
```

***

## 6. ดึง Pull Requests

### ดู PR ที่เปิดอยู่

```bash
gh pr list \
  --repo "$REPO_SLUG" \
  --state open \
  --limit 100 \
  --json number,title,author,state,mergeable,mergeStateStatus,isDraft,headRefName,baseRefName,createdAt,updatedAt
```

### ดึง PR ทั้งหมด

```bash
gh pr list \
  --repo "$REPO_SLUG" \
  --state all \
  --limit 1000 \
  --json number,title,author,state,mergeable,mergeStateStatus,isDraft,headRefName,baseRefName,createdAt,updatedAt,url
```

### ดู CI checks ของ PR

```bash
gh pr checks "$PR_NUMBER" --repo "$REPO_SLUG"
```

### ดึง PR ผ่าน REST API

```bash
gh api "/repos/$OWNER/$REPO/pulls?state=all&per_page=100"
```

***

## 7. Pagination สำหรับ PR มากกว่า 100 รายการ

GitHub REST API จำกัดผลลัพธ์ไม่เกิน 100 รายการต่อหน้า ให้ใช้ `--paginate` เพื่อให้ `gh` ตามหน้าให้เอง:

```bash
gh api --paginate \
  "/repos/$OWNER/$REPO/pulls?state=all&per_page=100"
```

### Export PR ทุกหน้าเป็น JSON array เดียว

`--paginate` จะ output เป็นหลาย JSON arrays ต่อกันหาก endpoint คืน array ต่อหน้า ดังนั้นต้องใช้ `--slurp` เพื่อรวม page outputs เป็น array แล้ว flatten:

```bash
gh api --paginate --slurp \
  "/repos/$OWNER/$REPO/pulls?state=all&per_page=100" \
  --jq 'flatten' \
  > "$OUTDIR/prs-raw.json"
```

### สร้าง PR JSON ที่เลือกเฉพาะฟิลด์สำคัญ

```bash
gh api --paginate --slurp \
  "/repos/$OWNER/$REPO/pulls?state=all&per_page=100" \
  --jq '
    flatten
    | map({
        pr_number: .number,
        title,
        state,
        draft: .draft,
        author: .user.login,
        head_branch: .head.ref,
        base_branch: .base.ref,
        created_at,
        updated_at,
        url: .html_url
      })
  ' \
  > "$OUTDIR/prs.json"
```

***

## 8. ส่งออก PR เป็น CSV

```bash
gh api --paginate \
  "/repos/$OWNER/$REPO/pulls?state=all&per_page=100" \
  --jq -r '
    ["pr_number","title","state","draft","author","head_branch","base_branch","created_at","updated_at","url"],
    (
      .[]
      | [
          .number,
          .title,
          .state,
          .draft,
          .user.login,
          .head.ref,
          .base.ref,
          .created_at,
          .updated_at,
          .html_url
        ]
    )
    | @csv
  ' \
  > "$OUTDIR/prs.csv"
```

> หากใช้ `gh api --paginate` โดยไม่ `--slurp`, `--jq` จะประมวลผลทีละหน้า และ header จะถูกเขียนซ้ำในทุก page  
> วิธีที่ปลอดภัยคือ export header แยกหนึ่งครั้ง แล้ว export records ต่อท้าย

```bash
printf '%s\n' \
  '"pr_number","title","state","draft","author","head_branch","base_branch","created_at","updated_at","url"' \
  > "$OUTDIR/prs.csv"

gh api --paginate \
  "/repos/$OWNER/$REPO/pulls?state=all&per_page=100" \
  --jq -r '
    .[]
    | [
        .number,
        .title,
        .state,
        .draft,
        .user.login,
        .head.ref,
        .base.ref,
        .created_at,
        .updated_at,
        .html_url
      ]
    | @csv
  ' \
  >> "$OUTDIR/prs.csv"
```

***

## 9. ดึง Reviews และ Comments

PR มีข้อมูลคนละประเภท จึงควร export แยกก่อน:

| ประเภท | Endpoint | ความหมาย |
|---|---|---|
| PR metadata | `/pulls` | ชื่อ, สถานะ, branch, ผู้สร้าง |
| Reviews | `/pulls/{PR}/reviews` | ผลรีวิว เช่น `APPROVED`, `CHANGES_REQUESTED` |
| Inline review comments | `/pulls/{PR}/comments` | ความเห็นบนบรรทัดโค้ด |
| Discussion comments | `/issues/{PR}/comments` | ความเห็นทั่วไปในหน้า PR |

### Review summaries

```bash
gh api --paginate \
  "/repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews?per_page=100" \
  --jq -r '
    ["pr_number","review_id","author","state","body","submitted_at","commit_id"],
    (
      .[]
      | [
          "'"$PR_NUMBER"'",
          .id,
          .user.login,
          .state,
          (.body | gsub("\n"; " ")),
          .submitted_at,
          .commit_id
        ]
    )
    | @csv
  ' \
  > "$OUTDIR/pr-$PR_NUMBER-reviews.csv"
```

### Inline review comments

```bash
gh api --paginate \
  "/repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments?per_page=100" \
  --jq -r '
    ["pr_number","comment_id","path","line","side","body","author","created_at","reply_to_id","diff_hunk"],
    (
      .[]
      | [
          "'"$PR_NUMBER"'",
          .id,
          .path,
          (.line // ""),
          (.side // ""),
          (.body | gsub("\n"; " ")),
          .user.login,
          .created_at,
          (.in_reply_to_id // ""),
          (.diff_hunk // "" | gsub("\n"; " "))
        ]
    )
    | @csv
  ' \
  > "$OUTDIR/pr-$PR_NUMBER-inline-comments.csv"
```

### Discussion comments

```bash
gh api --paginate \
  "/repos/$OWNER/$REPO/issues/$PR_NUMBER/comments?per_page=100" \
  --jq -r '
    ["pr_number","comment_id","body","author","created_at","updated_at","author_association"],
    (
      .[]
      | [
          "'"$PR_NUMBER"'",
          .id,
          (.body | gsub("\n"; " ")),
          .user.login,
          .created_at,
          .updated_at,
          .author_association
        ]
    )
    | @csv
  ' \
  > "$OUTDIR/pr-$PR_NUMBER-discussion-comments.csv"
```

> ใช้ `@csv` แล้วไม่ต้องทำ `gsub("\""; "\"\"")` เอง เพราะ `jq @csv` ทำ CSV escaping ให้แล้ว  
> การแทน newline ด้วยช่องว่างเป็นทางเลือกเพื่อให้อ่านง่ายใน spreadsheet แต่ไม่จำเป็นต่อความถูกต้องของ CSV

***

## 10. Export Reviews/Comments ของทุก PR

สร้างไฟล์ `export-pr-feedback.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

OWNER="ZyntroAI"
REPO="Development"
REPO_SLUG="$OWNER/$REPO"
OUTDIR="exports"

mkdir -p "$OUTDIR"

printf '%s\n' \
  '"pr_number","review_id","author","state","body","submitted_at","commit_id"' \
  > "$OUTDIR/all-pr-reviews.csv"

printf '%s\n' \
  '"pr_number","comment_type","comment_id","path","line","side","body","author","created_at","updated_at","reply_to_id","author_association","diff_hunk"' \
  > "$OUTDIR/all-pr-comments.csv"

gh pr list \
  --repo "$REPO_SLUG" \
  --state all \
  --limit 1000 \
  --json number \
  --jq '.[].number' |
while IFS= read -r PR_NUMBER; do
  echo "Exporting PR #$PR_NUMBER..." >&2

  gh api --paginate \
    "/repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews?per_page=100" \
    --jq -r --arg pr "$PR_NUMBER" '
      .[]
      | [
          $pr,
          .id,
          (.user.login // ""),
          (.state // ""),
          (.body // "" | gsub("\n"; " ")),
          (.submitted_at // ""),
          (.commit_id // "")
        ]
      | @csv
    ' \
    >> "$OUTDIR/all-pr-reviews.csv"

  gh api --paginate \
    "/repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments?per_page=100" \
    --jq -r --arg pr "$PR_NUMBER" '
      .[]
      | [
          $pr,
          "inline_review_comment",
          .id,
          (.path // ""),
          (.line // ""),
          (.side // ""),
          (.body // "" | gsub("\n"; " ")),
          (.user.login // ""),
          (.created_at // ""),
          (.updated_at // ""),
          (.in_reply_to_id // ""),
          (.author_association // ""),
          (.diff_hunk // "" | gsub("\n"; " "))
        ]
      | @csv
    ' \
    >> "$OUTDIR/all-pr-comments.csv"

  gh api --paginate \
    "/repos/$OWNER/$REPO/issues/$PR_NUMBER/comments?per_page=100" \
    --jq -r --arg pr "$PR_NUMBER" '
      .[]
      | [
          $pr,
          "discussion_comment",
          .id,
          "",
          "",
          "",
          (.body // "" | gsub("\n"; " ")),
          (.user.login // ""),
          (.created_at // ""),
          (.updated_at // ""),
          "",
          (.author_association // ""),
          ""
        ]
      | @csv
    ' \
    >> "$OUTDIR/all-pr-comments.csv"
done
```

รัน:

```bash
chmod +x export-pr-feedback.sh
./export-pr-feedback.sh
```

ผลลัพธ์:

```text
exports/
├── prs.csv
├── all-pr-reviews.csv
└── all-pr-comments.csv
```

***

## 11. รวมไฟล์ CSV ด้วย `csvstack`

`csvstack` ใช้รวมไฟล์ schema เดียวกันแบบต่อแถว ไม่ใช่ join ตามคีย์

```bash
csvstack \
  exports/pr-*-reviews.csv \
  > exports/all-pr-reviews.csv
```

### เก็บชื่อไฟล์ต้นทาง

```bash
csvstack \
  --filenames \
  -n source_file \
  exports/pr-*-reviews.csv \
  > exports/all-pr-reviews-with-source.csv
```

### ข้อควรระวัง

- ทุกไฟล์ควรมีชื่อคอลัมน์, ลำดับคอลัมน์ และจำนวนคอลัมน์เท่ากัน
- อย่าบันทึก output ให้ตรงกับ wildcard input เช่น `csvstack *.csv > merged.csv`
- ใช้ output คนละโฟลเดอร์ หรือ glob ให้จำเพาะ เช่น `exports/pr-*-reviews.csv`

***

## 12. เชื่อม CSV ด้วย `csvjoin`

### Inner Join

เก็บเฉพาะ PR ที่พบในทั้งสองฝั่ง:

```bash
csvjoin \
  -c pr_number \
  exports/prs.csv \
  exports/all-pr-reviews.csv \
  > exports/prs-with-reviews-inner.csv
```

### Left Join

เก็บ PR ทุกตัวจาก `prs.csv` แม้ไม่มี review:

```bash
csvjoin \
  --left \
  -c pr_number \
  exports/prs.csv \
  exports/all-pr-reviews.csv \
  > exports/prs-with-reviews.csv
```

### Join มากกว่าสองไฟล์

```bash
csvjoin \
  --left \
  -c pr_number \
  exports/prs.csv \
  exports/all-pr-reviews.csv \
  exports/all-pr-comments.csv \
  > exports/prs-full-report.csv
```

### หากชื่อ key ไม่เหมือนกัน

```bash
csvjoin \
  --left \
  -c "pr_number,pull_request_number,pr_id" \
  prs.csv \
  reviews.csv \
  comments.csv \
  > pr-report.csv
```

ชื่อคอลัมน์ใน `-c` ต้องเรียงตามไฟล์ที่ส่งเข้า `csvjoin`

***

## 13. ชื่อคอลัมน์ซ้ำจาก `csvjoin`

เมื่อมีคอลัมน์ชื่อเดียวกันในหลายไฟล์ เช่น `author`, `state`, `created_at`, `csvjoin` จะเติมเลข suffix เพื่อป้องกัน header ชนกัน เช่น:

```text
author
author2
author3

pr_number
pr_number2
pr_number3
```

ตรวจ header จริงเสมอ:

```bash
csvcut -n exports/prs-full-report.csv
```

### ตัด key ที่ซ้ำหลัง join

```bash
csvcut \
  -C pr_number2,pr_number3 \
  exports/prs-full-report.csv \
  > exports/prs-full-report-clean.csv
```

### แนวทางที่ดีกว่า: Rename ก่อน Join

ทำให้ column names มีความหมายชัดเจน:

```text
author       → pr_author
state        → pr_state
created_at   → pr_created_at

author       → review_author
state        → review_state
body         → review_body

author       → comment_author
body         → comment_body
```

ตัวอย่าง:

```bash
csvsql --query '
  SELECT
    pr_number,
    title,
    author AS pr_author,
    state AS pr_state,
    created_at AS pr_created_at
  FROM prs
' exports/prs.csv > exports/prs-clean.csv
```

```bash
csvsql --query '
  SELECT
    pr_number,
    author AS review_author,
    state AS review_state,
    body AS review_body,
    submitted_at AS review_submitted_at
  FROM reviews
' exports/all-pr-reviews.csv > exports/reviews-clean.csv
```

```bash
csvsql --query '
  SELECT
    pr_number,
    author AS comment_author,
    body AS comment_body,
    created_at AS comment_created_at
  FROM comments
' exports/all-pr-comments.csv > exports/comments-clean.csv
```

***

## 14. ป้องกัน Row Multiplication

### ปัญหา

หาก PR เดียวมี:

- 2 reviews
- 3 comments

การ join ตรง ๆ จะสร้าง:

$$
2 \times 3 = 6
$$

แถวสำหรับ PR เดียว เพราะ review ทุกตัวจับคู่กับ comment ทุกตัว

### ทางแก้: Aggregate ก่อน Join

ถ้าต้องการหนึ่งแถวต่อหนึ่ง PR ให้สรุป reviews และ comments เป็นหนึ่งแถวต่อ `pr_number` ก่อน

```bash
csvsql --query '
  SELECT
    pr_number,
    COUNT(*) AS review_count,
    SUM(CASE WHEN state = "APPROVED" THEN 1 ELSE 0 END) AS approved_count,
    SUM(CASE WHEN state = "CHANGES_REQUESTED" THEN 1 ELSE 0 END) AS changes_requested_count,
    MAX(submitted_at) AS last_review_at
  FROM reviews
  GROUP BY pr_number
' exports/all-pr-reviews.csv \
  > exports/reviews-summary.csv
```

```bash
csvsql --query '
  SELECT
    pr_number,
    COUNT(*) AS comment_count,
    COUNT(DISTINCT author) AS unique_commenters,
    MAX(created_at) AS last_comment_at
  FROM comments
  GROUP BY pr_number
' exports/all-pr-comments.csv \
  > exports/comments-summary.csv
```

จากนั้น join ตาราง summary:

```bash
csvjoin \
  --left \
  -c pr_number \
  exports/prs.csv \
  exports/reviews-summary.csv \
  exports/comments-summary.csv \
  | csvcut -C pr_number2,pr_number3 \
  > exports/pr-summary-report.csv
```

### ตรวจ key ซ้ำก่อน Join

```bash
csvsql --query '
  SELECT
    pr_number,
    COUNT(*) AS row_count
  FROM reviews
  GROUP BY pr_number
  HAVING COUNT(*) > 1
  ORDER BY row_count DESC
' exports/all-pr-reviews.csv
```

ถ้าต้องการ output หนึ่งแถวต่อ PR คำสั่งด้านบนควรไม่คืนผลลัพธ์สำหรับไฟล์ summary

### ทำไม `DISTINCT` ไม่ใช่คำตอบหลัก

`SELECT DISTINCT` ลบได้เฉพาะแถวที่ซ้ำเหมือนกันทั้งแถว แต่ไม่ป้องกัน cross-product ระหว่าง review/comment ที่เป็นคนละ record ควร aggregate หรือกำหนด grain ของ report ก่อน join เสมอ

***

## 15. DuckDB: ทางเลือกสำหรับ CSV ใหญ่

DuckDB เหมาะกับ:

- ไฟล์ CSV ระดับหลายร้อย MB ถึง GB
- SQL join และ aggregate ที่ซับซ้อน
- สร้างรายงานโดยไม่เกิด fan-out
- Query ซ้ำจากไฟล์เดิม
- แปลง CSV เป็น Parquet เพื่อให้ query เร็วขึ้น

### Query CSV โดยตรง

```bash
duckdb -c "
  SELECT *
  FROM read_csv_auto('exports/all-pr-comments.csv')
  LIMIT 20;
"
```

### Filter และ aggregate

```bash
duckdb -c "
  SELECT
    pr_number,
    type,
    COUNT(*) AS comment_count
  FROM read_csv_auto('exports/all-pr-comments.csv')
  GROUP BY pr_number, type
  ORDER BY comment_count DESC;
"
```

### สร้างรายงานหนึ่งแถวต่อ PR

```bash
duckdb -c "
  COPY (
    WITH
    reviews AS (
      SELECT
        pr_number,
        COUNT(*) AS review_count,
        COUNT(*) FILTER (WHERE state = 'APPROVED') AS approved_count,
        COUNT(*) FILTER (WHERE state = 'CHANGES_REQUESTED') AS changes_requested_count,
        MAX(submitted_at) AS last_review_at
      FROM read_csv_auto('exports/all-pr-reviews.csv')
      GROUP BY pr_number
    ),
    comments AS (
      SELECT
        pr_number,
        COUNT(*) AS comment_count,
        COUNT(DISTINCT author) AS unique_commenters,
        MAX(created_at) AS last_comment_at
      FROM read_csv_auto('exports/all-pr-comments.csv')
      GROUP BY pr_number
    )
    SELECT
      p.*,
      COALESCE(r.review_count, 0) AS review_count,
      COALESCE(r.approved_count, 0) AS approved_count,
      COALESCE(r.changes_requested_count, 0) AS changes_requested_count,
      r.last_review_at,
      COALESCE(c.comment_count, 0) AS comment_count,
      COALESCE(c.unique_commenters, 0) AS unique_commenters,
      c.last_comment_at
    FROM read_csv_auto('exports/prs.csv') AS p
    LEFT JOIN reviews AS r USING (pr_number)
    LEFT JOIN comments AS c USING (pr_number)
    ORDER BY p.pr_number
  )
  TO 'exports/pr-summary-report.csv'
  (HEADER, DELIMITER ',');
"
```

### จำกัด memory และเปิดใช้ disk spill

```bash
duckdb -c "
  SET memory_limit = '2GB';
  SET temp_directory = './duckdb-tmp';

  SELECT
    pr_number,
    COUNT(*) AS comment_count
  FROM read_csv_auto('exports/all-pr-comments.csv')
  GROUP BY pr_number
  ORDER BY comment_count DESC;
"
```

### เก็บข้อมูลเป็นฐาน DuckDB

```bash
duckdb exports/pr-data.duckdb -c "
  CREATE OR REPLACE TABLE prs AS
  SELECT *
  FROM read_csv_auto('exports/prs.csv');

  CREATE OR REPLACE TABLE reviews AS
  SELECT *
  FROM read_csv_auto('exports/all-pr-reviews.csv');

  CREATE OR REPLACE TABLE comments AS
  SELECT *
  FROM read_csv_auto('exports/all-pr-comments.csv');
"
```

### แปลง CSV เป็น Parquet

```bash
duckdb -c "
  COPY (
    SELECT *
    FROM read_csv_auto('exports/all-pr-comments.csv')
  )
  TO 'exports/all-pr-comments.parquet'
  (FORMAT PARQUET);
"
```

Query Parquet:

```bash
duckdb -c "
  SELECT
    pr_number,
    COUNT(*) AS comment_count
  FROM 'exports/all-pr-comments.parquet'
  GROUP BY pr_number
  ORDER BY comment_count DESC;
"
```

***

## 16. qsv สำหรับ CSV ใหญ่

### ตรวจ schema และจำนวนแถว

```bash
qsv headers exports/all-pr-comments.csv
qsv count exports/all-pr-comments.csv
```

### เลือกคอลัมน์

```bash
qsv select \
  pr_number,type,author,created_at,body \
  exports/all-pr-comments.csv \
  > exports/comments-selected.csv
```

### ค้นหาแบบไม่สนตัวพิมพ์

```bash
qsv search \
  -i security body \
  exports/all-pr-comments.csv \
  > exports/security-comments.csv
```

### Sort

```bash
qsv sort \
  -s pr_number,created_at \
  exports/all-pr-comments.csv \
  > exports/comments-sorted.csv
```

### สร้าง index

```bash
qsv index exports/all-pr-comments.csv
```

### สถิติ

```bash
qsv stats \
  --everything \
  exports/all-pr-comments.csv \
  > exports/comments-stats.csv
```

### Frequency table

```bash
qsv frequency \
  type \
  exports/all-pr-comments.csv \
  > exports/comment-type-frequency.csv
```

***

## 17. Miller (`mlr`) สำหรับ Data Pipeline

### แสดงเป็นตาราง

```bash
mlr --icsv --opprint \
  cat exports/all-pr-comments.csv \
  | head -n 30
```

### Filter PR และประเภทข้อมูล

```bash
mlr --icsv --ocsv \
  filter '$pr_number == "123" && $comment_type == "inline_review_comment"' \
  exports/all-pr-comments.csv \
  > exports/pr-123-inline-comments.csv
```

### เลือกและ rename fields

```bash
mlr --icsv --ocsv \
  cut -f pr_number,comment_type,author,created_at,body \
  then rename created_at,comment_created_at \
  exports/all-pr-comments.csv \
  > exports/comments-clean.csv
```

### นับ comments ต่อ PR

```bash
mlr --icsv --ocsv \
  stats1 -a count -f comment_id -g pr_number \
  exports/all-pr-comments.csv \
  > exports/comment-count-per-pr.csv
```

***

## 18. ตรวจคุณภาพและความครบถ้วน

### ตรวจ header

```bash
csvcut -n exports/prs.csv
csvcut -n exports/all-pr-reviews.csv
csvcut -n exports/all-pr-comments.csv
```

### ตรวจจำนวนแถว

```bash
csvstat --count exports/prs.csv
csvstat --count exports/all-pr-reviews.csv
csvstat --count exports/all-pr-comments.csv
csvstat --count exports/pr-summary-report.csv
```

### หา PR ที่มีมากกว่าหนึ่งแถวใน report

```bash
duckdb -c "
  SELECT
    pr_number,
    COUNT(*) AS row_count
  FROM read_csv_auto('exports/pr-summary-report.csv')
  GROUP BY pr_number
  HAVING COUNT(*) > 1
  ORDER BY row_count DESC;
"
```

หาก report ต้องมีหนึ่งแถวต่อ PR คำสั่งนี้ควรได้ผลลัพธ์ว่าง

### ตรวจจำนวน PR ก่อนและหลัง

```bash
duckdb -c "
  SELECT COUNT(*) AS source_pr_count
  FROM read_csv_auto('exports/prs.csv');
"

duckdb -c "
  SELECT COUNT(*) AS report_pr_count
  FROM read_csv_auto('exports/pr-summary-report.csv');
"
```

หาก `prs.csv` มี `pr_number` ไม่ซ้ำ และรายงานใช้ `LEFT JOIN` กับ tables ที่ aggregate แล้ว จำนวนควรเท่ากัน

***

## 19. Workflow ที่แนะนำ

### งานขนาดเล็กถึงกลาง

```text
gh api / gh pr list
  → CSV exports
  → csvstack
  → csvsql aggregate
  → csvjoin --left
  → csvcut cleanup
  → CSV report
```

เหมาะเมื่อข้อมูลไม่ใหญ่มาก ต้องการคำสั่งที่อ่านง่าย และแยกแต่ละขั้นตอนตรวจสอบได้

### งานขนาดใหญ่หรือรายงานซับซ้อน

```text
gh api / gh pr list
  → raw CSV exports
  → DuckDB
      → clean / normalize
      → aggregate
      → left join
      → quality checks
      → CSV + Parquet + .duckdb
```

เหมาะเมื่อมี PR, comments หรือ reviews จำนวนมาก, ต้อง join หลายตาราง, ต้องการป้องกัน row multiplication อย่างจริงจัง, หรือต้องทำรายงานซ้ำเป็นระยะ

***

## 20. Checklist ก่อนส่งออกรายงาน

- [ ] `gh auth status` ผ่าน และ account มีสิทธิ์อ่าน repo
- [ ] ตรวจว่าดึง PR ครบทุกหน้า (`--paginate`)
- [ ] ใช้ `per_page=100` กับ GitHub REST endpoints
- [ ] ระบุ `pr_number` ในทุก record ของ reviews/comments
- [ ] แยก review summaries, inline comments และ discussion comments ให้ชัดเจน
- [ ] ใช้ `jq @csv` เพื่อ escape CSV อย่างถูกต้อง
- [ ] ใช้ `csvstack` เฉพาะไฟล์ที่ schema เดียวกัน
- [ ] ตรวจ header ด้วย `csvcut -n` ก่อน `csvjoin`
- [ ] Rename columns ที่ซ้ำก่อน join หรือ cleanup suffix หลัง join
- [ ] Aggregate reviews/comments เป็นหนึ่งแถวต่อ `pr_number` ก่อน join
- [ ] ตรวจหา `pr_number` ซ้ำใน output report
- [ ] เปรียบเทียบจำนวน PR ก่อนและหลังสร้าง report
- [ ] เก็บ raw export ไว้ต่างหากจาก cleaned/summary/report outputs
- [ ] ไม่ commit token, PAT, credential, export ที่มีข้อมูลอ่อนไหว หรือ log ที่มี secret

***

## 21. โครงสร้างโฟลเดอร์แนะนำ

```text
github-pr-report/
├── env.sh
├── export-pr-feedback.sh
├── report.sql
├── raw/
│   ├── prs-raw.json
│   ├── prs.csv
│   ├── all-pr-reviews.csv
│   └── all-pr-comments.csv
├── processed/
│   ├── reviews-summary.csv
│   ├── comments-summary.csv
│   ├── pr-summary-report.csv
│   └── all-pr-comments.parquet
├── database/
│   └── pr-data.duckdb
└── logs/
    └── export.log
```

***

## 22. คำสั่งสั้นที่ใช้บ่อย

```bash
# Login GitHub
gh auth login && gh auth setup-git

# PR ทั้งหมดเกิน 100 รายการ
gh api --paginate \
  "/repos/$OWNER/$REPO/pulls?state=all&per_page=100"

# Commit หนึ่งรายการ
gh api "/repos/$OWNER/$REPO/commits/$SHA"

# รวมไฟล์ชนิดเดียวกัน
csvstack --filenames -n source_file \
  exports/pr-*-reviews.csv \
  > exports/all-pr-reviews.csv

# ดู header
csvcut -n exports/prs.csv

# Query CSV ใหญ่
duckdb -c "
  SELECT pr_number, COUNT(*)
  FROM read_csv_auto('exports/all-pr-comments.csv')
  GROUP BY pr_number;
"

# Export SQL query เป็น CSV
duckdb -c "
  COPY (
    SELECT *
    FROM read_csv_auto('exports/prs.csv')
  )
  TO 'exports/prs-copy.csv'
  (HEADER, DELIMITER ',');
"

# ตรวจ PR ซ้ำใน report
duckdb -c "
  SELECT pr_number, COUNT(*)
  FROM read_csv_auto('exports/pr-summary-report.csv')
  GROUP BY pr_number
  HAVING COUNT(*) > 1;
"
```

***

## 23. ข้อจำง่าย

- `csvstack` = **ต่อแถว** ของไฟล์ schema เดียวกัน  
- `csvjoin` = **เชื่อมคอลัมน์** ตาม key  
- `--left` = เก็บทุกแถวจากไฟล์แรก  
- `--paginate` = ดึง GitHub API มากกว่า 100 รายการ  
- `@csv` = ให้ `jq` escape ค่าภายใน CSV  
- `GROUP BY pr_number` = ทำให้ summary เหลือหนึ่งแถวต่อ PR  
- Aggregate ก่อน join = ป้องกัน row multiplication  
- DuckDB = ตัวเลือกที่ดีสุดเมื่อข้อมูลใหญ่หรือ SQL ซับซ้อน  
- Parquet = เหมาะกับ query ซ้ำและไฟล์ขนาดใหญ่

