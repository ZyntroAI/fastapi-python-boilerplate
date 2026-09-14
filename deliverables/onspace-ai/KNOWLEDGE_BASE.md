# Knowledge Base — Patterns & Limits

หลักการออกแบบ + เกณฑ์/ข้อจำกัดสำหรับ stack นี้

## Core Design Principles

1. **Cost-First**: Avoid request → optimize → retry
2. **Defense in Depth**: Cache + Circuit Breaker + Fallback + Timeout
3. **Token Discipline**: Measure → Limit → Compress → Reuse
4. **Observable**: ทุก error/latency/token/cache-hit มี metric
5. **Safe Automation**: ไม่ auto-merge secrets/auth/infra

## Retryable vs Non-retryable

| Status | Retryable | เหตุผล |
|--------|-----------|--------|
| 408, 429, 502, 503, 504 | ✅ | ชั่วคราว — ลองใหม่ได้ |
| 400, 401, 403, 422 | ❌ | ผิดถาวร — ไม่เสีย cost ลองใหม่ |

Fallback router: **non-retryable → หยุดทันที** (ไม่เรียก provider ตัวถัดไป)

## Circuit Breaker States

- **CLOSED**: ปล่อย request ปกติ
- **OPEN**: ล้มเกิน threshold → block ทั้งหมด (cooldown 30s)
- **HALF-OPEN**: หลัง cooldown ลอง 1 request → สำเร็จ=CLOSED / ล้ม=OPEN

## Cache Hierarchy

```
L0 Dedup → L1 Browser → L2 CDN → L3 Redis → L4 Context → L5 Result
```

## Resilience

- **Redis fail-open**: Redis ล่ม → cache miss / ไม่ crash
- **Fallback**: primary → secondary → degraded (คืน 503)
- **Timeout + bounded retry**: กันงานค้าง

## Observability Metrics

```
onspaceai_api_requests_total / latency_seconds
onspaceai_cache_hits_total / misses_total
onspaceai_fallback_total / degraded_responses_total
onspaceai_tokens_total / tokens_saved
```

## Security

- Auth (X-API-Key) — ข้าม /health /metrics /docs
- X-Request-ID ทุกรีเควสต์
- Redis TLS + auth ใน production
- ไม่ hardcode key — pydantic-settings จาก .env
