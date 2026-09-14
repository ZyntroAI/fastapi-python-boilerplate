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
