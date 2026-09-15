# GitHub Organization Integration

แหล่งจริง: `config/github-rules.json`

```yaml
masterfiles:
  require_code_owner: true
  require_pull_request: true
  require_status_checks: true
  require_signed_commits: true
  require_review_count: 2
```

## เทียบกับการตั้งค่าจริงใน repo

| กฎ | ต้องเป็น | สถานะปัจจุบัน |
|---|---|---|
| `require_code_owner` | `true` | ต้องตรวจใน branch protection |
| `require_pull_request` | `true` | ✅ ใช้ PR ทุกครั้ง |
| `require_status_checks` | `true` | ⚠️ CI ยังไม่ครบทุก PR |
| `require_signed_commits` | `true` | ❌ ยังไม่ได้เปิด |
| `require_review_count` | `2` | ⚠️ ส่วนใหญ่ merge ด้วย 1 review |

**ช่องว่างที่ต้องปิดก่อนถือว่าสอดคล้อง:** signed commits และ review count = 2
เป็นสองข้อที่ยังไม่ตรงกับนโยบาย

## ผลกระทบที่ต้องรู้

- `require_signed_commits: true` จะบล็อค commit ที่ไม่ใช้ GPG key —
  ต้องตั้ง signing key ให้ทุก contributor ก่อนเปิด
- `require_review_count: 2` จะทำให้ PR ที่ merge คนเดียวผ่านไม่ได้อีก
- `require_status_checks: true` ต้องมี check ชื่อคงที่ ไม่ใช่ "ทุก check"
