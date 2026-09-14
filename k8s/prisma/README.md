# 🛡️ เพิ่มระบบจำกัดอัตราการเรียกใช้ (Rate Limit)

เพิ่มทั้ง **โมเดลในฐานข้อมูล** และ **ชั้นตรวจสอบแบบนำไปใช้จริง** ครับ ✅

---

## 📄 1. เพิ่มโมเดลใน `prisma/schema.prisma`

วางต่อท้ายไฟล์ได้เลยครับ

```prisma
// ──────────────────────────────────────────────
// 📊 บันทึกการเรียกใช้ API สำหรับ Rate Limit
// ──────────────────────────────────────────────
model ApiUsage {
  id          String   @id @default(uuid())
  apiKeyId    String?
  userId      String?
  endpoint    String   // เช่น "/api/v1/projects"
  method      String   // "GET", "POST", etc.
  statusCode  Int      // 200, 401, 429...
  ipAddress   String?
  userAgent   String?
  timestamp   DateTime @default(now()) @db.Timestamp(6)

  // ความสัมพันธ์
  apiKey      ApiKey?  @relation(fields: [apiKeyId], references: [id], onDelete: Cascade)

  // ดัชนีสำหรับค้นหา+นับแบบรวดเร็ว
  @@index([apiKeyId, timestamp])
  @@index([userId, timestamp])
  @@index([ipAddress, timestamp])
  @@map("api_usage")
}

// ──────────────────────────────────────────────
// ⚙️ กฎจำกัดอัตราการเรียกใช้
// ──────────────────────────────────────────────
model RateLimitRule {
  id          String   @id @default(uuid())
  identifier  String   @unique // "default", "user:{id}", "key:{id}", "ip:{xxx}"
  limit       Int      // จำนวนสูงสุด
  windowSec   Int      // ช่วงเวลาเป็นวินาที (เช่น 60 = 1 นาที)
  createdAt   DateTime @default(now()) @db.Timestamp(6)
  updatedAt   DateTime @updatedAt @db.Timestamp(6)

  @@map("rate_limit_rules")
}
```

### ✅ โครงสร้างที่ได้
- **`ApiUsage`** — บันทึกทุกครั้งที่เรียกใช้ • ผู้เรียก • ปลายทาง • เวลา
- **`RateLimitRule`** — กฎแบบยืดหยุ่น • แยกตามคีย์/ผู้ใช้/IP หรือค่าเริ่มต้นระบบ

---

## 🧩 2. ไลบรารีตรวจสอบ Rate Limit (`lib/rate-limit.ts`)

สร้างไฟล์นี้เพื่อนำไปใช้ตรงกลางครับ

```typescript
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

// ⚙️ ค่าเริ่มต้น ถ้าไม่มีกฎในฐานข้อมูล
const DEFAULT_LIMIT = 100      // จำนวนครั้ง
const DEFAULT_WINDOW = 60 * 60 // ต่อ 1 ชั่วโมง (วินาที)

export interface RateLimitResult {
  allowed: boolean
  limit: number
  remaining: number
  resetAt: Date
}

// 🔹 ตรวจสอบและบันทึกการเรียกใช้
export async function checkRateLimit(
  identifier: string, // เช่น "key:sk_xxx", "user:uid", "ip:1.2.3.4"
  endpoint: string,
  method: string,
  ipAddress?: string,
  userAgent?: string
): Promise<RateLimitResult> {
  // 1. ดึงกฎที่ใช้
  const rule = await prisma.rateLimitRule.findUnique({
    where: { identifier },
  })
  const limit = rule?.limit ?? DEFAULT_LIMIT
  const windowSec = rule?.windowSec ?? DEFAULT_WINDOW

  // 2. คำนวณช่วงเวลา
  const now = new Date()
  const windowStart = new Date(now.getTime() - windowSec * 1000)

  // 3. นับจำนวนการเรียกในช่วงเวลานี้
  const count = await prisma.apiUsage.count({
    where: {
      OR: [
        { apiKey: { prefix: identifier.replace('key:', '') } },
        { userId: identifier.startsWith('user:') ? identifier.slice(5) : undefined },
        { ipAddress: identifier.startsWith('ip:') ? identifier.slice(3) : undefined },
      ],
      timestamp: { gte: windowStart },
      statusCode: { not: 429 }, // ไม่นับคำขอที่ถูกปฏิเสธแล้ว
    },
  })

  const remaining = Math.max(0, limit - count)
  const resetAt = new Date(now.getTime() + windowSec * 1000)

  // 4. บันทึกการเรียกใช้
  await prisma.apiUsage.create({
    data: {
      endpoint,
      method,
      ipAddress,
      userAgent,
      statusCode: remaining > 0 ? 200 : 429,
      timestamp: now,
    },
  })

  return { allowed: remaining > 0, limit, remaining, resetAt }
}

// 🔹 ตัวช่วยสร้างส่วนหัวตอบกลับ
export function getRateLimitHeaders(result: RateLimitResult): Record<string, string> {
  return {
    'X-RateLimit-Limit': String(result.limit),
    'X-RateLimit-Remaining': String(result.remaining),
    'X-RateLimit-Reset': String(Math.floor(result.resetAt.getTime() / 1000)),
  }
}
```

---

## 🎯 3. ตัวอย่างนำไปใช้ใน API Route

### Express / Node
```typescript
import { checkRateLimit, getRateLimitHeaders } from '@/lib/rate-limit'

app.use(async (req, res, next) => {
  // ระบุผู้เรียก — จากคีย์ API หรือ ผู้ใช้ที่เข้าสู่ระบบ หรือ IP
  const identifier = req.user?.id
    ? `user:${req.user.id}`
    : req.headers['x-api-key']
    ? `key:${String(req.headers['x-api-key']).slice(0, 8)}`
    : `ip:${req.ip}`

  const result = await checkRateLimit(
    identifier,
    req.path,
    req.method,
    req.ip,
    req.headers['user-agent']
  )

  res.setHeaders(getRateLimitHeaders(result))

  if (!result.allowed) {
    return res.status(429).json({
      error: 'Too Many Requests',
      message: `ลองใหม่ภายใน ${Math.ceil((result.resetAt.getTime() - Date.now()) / 60000)} นาที`,
    })
  }

  next()
})
```

### FastAPI (Python) — ถ้าใช้ด้านนี้
```python
# อ้างอิงได้จากตาราง ApiUsage + RateLimitRule เดียวกัน
```

---

## 🚀 4. สร้างตาราง & ข้อมูลเริ่มต้น
```bash
npx prisma migrate dev --name add_rate_limit
```

### 📋 ข้อมูลเริ่มต้น (Seed)
เพิ่มใน `prisma/seed.ts` เพื่อให้มีกฎเริ่มต้นทันที

```typescript
await prisma.rateLimitRule.upsert({
  where: { identifier: 'default' },
  update: {},
  create: {
    identifier: 'default',
    limit: 100,      // 100 ครั้ง
    windowSec: 3600, // ต่อ 1 ชั่วโมง
  },
})
```

รัน:
```bash
npx prisma db seed
```

---

## ✅ สรุปคุณสมบัติ
| คุณสมบัติ | ทำงานอย่างไร |
|---|---|
| แยกกฎตามประเภท | คีย์ API / ผู้ใช้ / IP Address |
| นับย้อนหลังแบบเลื่อน | ไม่ต้องรอชั่วโมงถัดไป |
| บันทึกประวัติครบถ้วน | วิเคราะห์การใช้งานภายหลังได้ |
| ส่วนหัวมาตรฐาน `X-RateLimit-*` | เข้ากันได้กับเครื่องมือทั่วไป |
| ปรับกฎแบบเรียลไทม์ | แก้ตาราง `rate_limit_rules` ได้ทันที |

ต้องการเพิ่ม **กฎแยกตามระดับผู้ใช้ (ฟรี/โปร/องค์กร)** หรือ **แคชในหน่วยความจำเพื่อลดการคิวรีฐานข้อมูล** ไหมครับ? ⚡📊✅
