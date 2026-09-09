# GitHub Actions Workflow Commands — Reference (2026)

Command ที่ใช้พับ log / สร้าง annotation / เขียนผลลัพธ์ภายใน workflow step รองรับทั้ง Bash และ PowerShell

## กลุ่ม/พับ log

| Command | การใช้งาน |
|---------|-----------|
| `::group::<name>` | เริ่มกลุ่ม collapsible ใน log |
| `::endgroup::` | จบกลุ่ม |

```bash
echo "::group::Azure Deployment"
az deployment group create ...
echo "::endgroup::"
```

## Annotation — notice / warning / error

```
::notice title=<title>::<message>
::warning title=<title>::<message>
::error title=<title>::<message>
```

รองรับ property: `file`, `line`, `endLine`, `col`, `endColumn` ต่อท้าย title

```bash
echo "::notice title=Deployment::Succeeded"
echo "::warning file=infra/main.bicep,line=12::Resource name not unique"
echo "::error title=Deploy Failed::Check what-if output"
```

## ตั้งค่าตัวแปร/env

```bash
# ใช้ได้ใน steps ถัดไปของ job เดียวกัน
echo "RG_NAME=rg-prod-01" >> "$GITHUB_ENV"

# ใช้ได้เฉพาะ job นี้ (env ระดับ step)
echo "::set-env name=NAME::value"   # (deprecated — ใช้ GITHUB_ENV)
```

## ส่งออกจาก step ($GITHUB_OUTPUT)

step ต้องประกาศ `id:` ก่อน แล้วอ่านด้วย `steps.<id>.outputs.<name>`

```bash
echo "storage_id=...value..." >> "$GITHUB_OUTPUT"
```

```yaml
- id: deploy
  run: echo "storage=stappdemo01" >> "$GITHUB_OUTPUT"
- run: echo "storage=${{ steps.deploy.outputs.storage }}"
```

## Job / Step Summary ($GITHUB_STEP_SUMMARY)

เขียน Markdown ที่แสดงในหน้าสรุปของ run

```bash
cat <<'EOF' >> "$GITHUB_STEP_SUMMARY"
## Deploy Result
- **RG:** `rg-prod-01`
- **Status:** ✅ Success
EOF
```

## อื่น ๆ

- `::add-mask::<value>` — ซ่อนค่าใน log (ใช้กับ secret/ค่าอ่อนไหว)
- `::save-state name=NAME::value` / `$STATE_NAME` — เก็บค่าระหว่าง pre/post ของ action
- `::stop-commands::<token>` / `::<token>::` — ปิด/เปิดการประมวลผล command ชั่วคราว

## หมายเหตุ

- Command ตัวพิมพ์เล็กก็ใช้ได้ (`::group::`, `::error::`)
- `::set-env`/`::set-output`/`::add-path` เป็น **deprecated** — ใช้ `$GITHUB_ENV`, `$GITHUB_OUTPUT`, `$GITHUB_PATH` แทน
- ดูเพิ่ม: [GitHub Docs — Workflow commands](https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions)
