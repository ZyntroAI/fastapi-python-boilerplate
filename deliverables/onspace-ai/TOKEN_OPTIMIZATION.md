# Token Optimization Guide

วิธีลดค่าใช้จ่าย/เวลา/rate-limit ของ LLM — เน้น "วัด → จำกัด → บีบอัด → ใช้ซ้ำ"

## หลักการ

> Tokens = Money + Latency + Rate Limits
> Prompt ที่ไม่ได้ optimize = 2–5× cost

## Checklist

1. **Cache ทุกอย่าง** — prompt เดิม → 0 tokens (Redis key จาก SHA-256)
2. **System prompt สั้น** — ตรงประเด็น ไม่มีน้ำ
3. **Trim history** — เก็บเฉพาะ turns ที่เกี่ยวข้อง (`trim_history`)
4. **ตัด redundancy** — ไม่มีคำสั่งซ้ำ (`deduplicate_messages`)
5. **Reject เร็ว** — payload ใหญ่เกิน → 413 ก่อนเรียก provider (`budget.check`)
6. **Reuse fragments** — cache context ยาวๆ ที่ใช้ซ้ำ

## Modules

### Context Compiler (`app/context_compiler.py`)

| ฟังก์ชัน | หน้าที่ |
|---------|--------|
| `clean_text` | ตัด whitespace + บรรทัดว่างซ้ำ |
| `deduplicate_messages` | ลบข้อความซ้ำติดกัน |
| `trim_history` | เก็บ last N turns |
| `estimate_tokens` | ประมาณ token จาก UTF-8 bytes (~3.5 chars/token) |
| `compile_context` | รวมทั้งหมด + นับ estimated_tokens + flag over_budget |

### Token Budget (`app/token_budget.py`)

- `MODEL_LIMITS`: gpt-4o 128k / claude-3-opus 200k / gemini 1M / mini 32k
- `check()`: hard reject เกินก่อนเรียก
- `truncate()`: ตัด message เก่าออกจนไม่เกิน + นับ `TOKEN_SAVED`

## Metrics

```
onspaceai_tokens_total        # token ที่ประมวล (ต่อ model)
onspaceai_tokens_saved        # token ที่ประหยัดได้จากการ optimize
onspaceai_cache_hits_total    # cache hit
```

## Example

```python
from app.context_compiler import compile_context
from app.token_budget import TokenBudget

ctx = compile_context(sys, messages, max_tokens=1024)   # clean/dedup/trim
budget = TokenBudget("gpt-4o")
if not budget.check(ctx["estimated_tokens"]):
    raise HTTPException(413)                            # reject เร็ว
ctx = budget.truncate(ctx)                              # ถ้ายังเกิน → ตัด
```
