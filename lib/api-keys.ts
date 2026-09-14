import { crypto } from '@noble/hashes/crypto'
import { sha256 } from '@noble/hashes/sha256'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

// 🔹 สร้างคีย์ใหม่ — คืนค่า (ข้อความจริง + บันทึกลง DB)
export async function createApiKey(userId: string, name: string, scopes: string[] = ['read']) {
  const rawBytes = crypto.getRandomValues(new Uint8Array(32))
  const rawKey = `sk_${Buffer.from(rawBytes).toString('base64url')}`
  const keyHash = Buffer.from(sha256(rawKey)).toString('hex')
  const prefix = `${rawKey.slice(0, 8)}...${rawKey.slice(-4)}`

  const record = await prisma.apiKey.create({
    data: { userId, name, prefix, keyHash, scopes },
  })

  return { rawKey, record }
}

// 🔹 ตรวจสอบคีย์เมื่อมีการเรียกใช้
export async function verifyApiKey(rawKey: string) {
  const keyHash = Buffer.from(sha256(rawKey)).toString('hex')
  const record = await prisma.apiKey.findUnique({ where: { keyHash } })

  if (!record || record.isRevoked) return null
  if (record.expiresAt && record.expiresAt < new Date()) return null

  // อัปเดตเวลาเรียกใช้ล่าสุด
  await prisma.apiKey.update({
    where: { id: record.id },
    data: { lastUsedAt: new Date() },
  })

  return record
}
