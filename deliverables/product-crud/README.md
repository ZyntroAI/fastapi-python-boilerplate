# product-crud — Products CRUD (Prisma + Express + React)

ชุด deliverable แบบ self-contained สำหรับงาน CRUD สินค้า — backend (Express + Prisma + Zod) และ frontend (React + TanStack Query + React Hook Form) ใช้ **Zod schema เดียวกัน** ทั้งสองฝั่ง จึงไม่ต้อง sync type ด้วยมือ

## โครงสร้าง

```
product-crud/
├── docker-compose.yml             # Postgres 16 สำหรับ dev
├── server/                        # Express + Prisma + Zod
│   ├── prisma/schema.prisma       # Product model + ProductStatus enum + indexes
│   ├── prisma/seed.ts             # ข้อมูลตัวอย่าง 30 รายการ (idempotent)
│   ├── Dockerfile                 # production image (3 stage, non-root)
│   ├── docker-entrypoint.sh       # apply schema ก่อน start + exec ต่อ
│   └── src/
│       ├── lib/zod/product.schema.ts   # single source of truth ของ contract
│       ├── lib/pagination.ts           # skip/take, meta, where builder (pure)
│       ├── lib/errors.ts               # HttpError + helpers
│       ├── lib/prisma.ts               # PrismaClient singleton
│       ├── services/product.service.ts # business logic + row → DTO
│       ├── controllers/product.controller.ts
│       ├── routes/product.routes.ts
│       ├── app.ts                      # CORS + JSON + central error handler
│       └── index.ts                    # listen + graceful shutdown
└── web/                           # Vite + React + TanStack Query
    └── src/
        ├── types/product.ts       # mirror Zod schema + response types
        ├── lib/api.ts             # fetch wrapper → ApiError
        ├── lib/products.api.ts    # endpoint functions + Zod parse
        ├── hooks/queryKeys.ts     # cache keys (params อยู่ใน key)
        ├── hooks/useProducts.ts   # queries + keepPreviousData
        ├── hooks/useProductMutations.ts  # create/update/delete
        ├── components/ProductsTable.tsx
        ├── components/ProductFormModal.tsx
        └── pages/ProductsPage.tsx
```

## Data model

| Field | Type | หมายเหตุ |
|---|---|---|
| `id` | `String` | `cuid()` |
| `name` | `String` | 1–200 ตัวอักษร |
| `sku` | `String` | **unique**, `[A-Za-z0-9._-]+`, ≤64 |
| `description` | `String?` | ≤2000 |
| `price` | `Decimal(10,2)` | ส่งออกเป็น `number` |
| `stock` | `Int` | default `0` |
| `status` | `ProductStatus` | `DRAFT` / `ACTIVE` / `ARCHIVED` |
| `createdAt` / `updatedAt` | `DateTime` | `updatedAt` อัปเดตอัตโนมัติ |

Index บน `name`, `status`, `createdAt` เพื่อรองรับ search, filter และ default sort

## API

| Method | Path | คำอธิบาย |
|---|---|---|
| `GET` | `/api/products` | list + pagination + search + filter + sort |
| `GET` | `/api/products/:id` | ดึงรายการเดียว |
| `POST` | `/api/products` | สร้างใหม่ → `201` |
| `PUT` | `/api/products/:id` | แก้ไข (partial) |
| `DELETE` | `/api/products/:id` | ลบ → `{ id }` |
| `GET` | `/health` | health check |

**Query params** ของ `GET /api/products`

| Param | Default | กติกา |
|---|---|---|
| `page` | `1` | ≥ 1 |
| `pageSize` | `20` | 1–100 |
| `search` | — | ค้นแบบ case-insensitive ใน `name`, `sku`, `description` |
| `status` | — | `DRAFT` \| `ACTIVE` \| `ARCHIVED` |
| `sortBy` | `createdAt` | `name` \| `price` \| `stock` \| `createdAt` \| `updatedAt` |
| `sortDir` | `desc` | `asc` \| `desc` |

**Response**

```json
{
  "items": [ { "id": "p_1", "name": "Torque Wrench", "sku": "TW-100",
               "description": null, "price": 49.99, "stock": 12,
               "status": "ACTIVE",
               "createdAt": "2026-01-01T00:00:00.000Z",
               "updatedAt": "2026-01-01T00:00:00.000Z" } ],
  "meta": { "page": 1, "pageSize": 20, "total": 1, "totalPages": 1,
            "hasNext": false, "hasPrev": false }
}
```

**Error shape** (ทุกกรณี)

```json
{ "error": { "code": "BAD_REQUEST", "message": "Validation failed", "details": { } } }
```

รหัสที่ใช้: `BAD_REQUEST` (400), `NOT_FOUND` (404), `CONFLICT` (409 — SKU ซ้ำ), `INTERNAL` (500)

## Quick start (คำสั่งเดียว)

ต้องมี Docker Desktop หรือ Docker Engine + Compose v2

```bash
cd server
npm install
npm run db:up        # สตาร์ท Postgres + migrate + seed ให้ครบในคำสั่งเดียว
npm run dev          # http://localhost:4000
```

`db:up` ทำให้ทั้งสามอย่างตามลำดับ: `docker compose up -d --wait` → `prisma migrate` → `prisma db seed`

จากนั้นเปิด frontend อีก terminal:

```bash
cd web
npm install
npm run dev          # http://localhost:5173
```

### คำสั่งจัดการฐานข้อมูล

| คำสั่ง | ทำอะไร |
|---|---|
| `npm run db:up` | สตาร์ท Postgres + migrate + seed |
| `npm run db:down` | หยุด container (ข้อมูลยังอยู่ใน named volume) |
| `npm run db:reset` | ลบ volume แล้วเริ่มใหม่ทั้งหมด — **ข้อมูลหาย** |

`docker-compose.yml` อยู่ที่ root ของ deliverable ใช้ image `postgres:16-alpine` พร้อม named volume `product_crud_pgdata` ข้อมูลจึงไม่หายเมื่อ `db:down`

ค่า credentials ใน compose ตรงกับ `server/.env.example` แล้ว (`postgres` / `postgres` / db `products`) ไม่ต้องแก้อะไรเพิ่ม

### Healthcheck

compose มี healthcheck ด้วย `pg_isready` และ npm script เรียกด้วย `up -d --wait` จึงรอจน Postgres รับ connection จริงก่อนรัน migrate — กันอาการ migrate ล้ม intermittently ที่เกิดจาก `up -d` เฉย ๆ ที่ return ก่อน database พร้อม

## Setup แบบ manual (ไม่ใช้ Docker)

ถ้ามี Postgres อยู่แล้ว ข้าม compose ได้เลย

```bash
cd server
cp .env.example .env          # ตั้ง DATABASE_URL ให้ชี้ไปที่ Postgres ของคุณ
npm install
npm run prisma:generate
npm run prisma:migrate        # สร้างตาราง products
npm run prisma:seed           # ใส่ข้อมูลตัวอย่าง 30 รายการ (ไม่บังคับ แต่แนะนำ)
npm run dev
```

แล้วรัน frontend แยกอีก terminal:

```bash
cd web
cp .env.example .env          # VITE_API_BASE_URL=http://localhost:4000
npm install
npm run dev
```

Vite ตั้ง proxy `/api` ไปที่ `http://localhost:4000` ไว้ให้แล้ว ถ้าไม่ตั้ง `VITE_API_BASE_URL` ก็ยังเรียก API ผ่าน proxy ได้

## Production Docker image (backend)

```bash
cd server
npm run docker:build          # docker build -t product-crud-server:local .
npm run docker:run            # รันที่ http://localhost:4000
```

หรือตรง ๆ:

```bash
docker build -t product-crud-server:local ./server
docker run --rm -p 4000:4000 \
  -e DATABASE_URL="[REDACTED]" \
  product-crud-server:local
```

### โครงสร้าง image (3 stage)

| Stage | ทำอะไร |
|---|---|
| `deps` | `npm ci` ติดตั้งครบ + ติดตั้ง `openssl` ที่ Prisma engine ต้องใช้ |
| `build` | `prisma generate` แล้ว `npm run build` → `dist/` |
| `runtime` | `npm ci --omit=dev` + `prisma generate` + คัดลอก `dist/` มาเท่านั้น |

ขนาดลดลงเพราะ stage สุดท้ายไม่มี TypeScript, vitest, supertest และ image รันด้วย user `nodejs` (uid 1001) ไม่ใช่ root

### Entrypoint และการ apply schema

`docker-entrypoint.sh` apply Prisma schema ให้ก่อนสตาร์ท server แล้ว `exec` ต่อเพื่อให้ signal ถึงตัว Node โดยตรง (มี `tini` เป็น PID 1)

โมดูลนี้ **ยังไม่มี `prisma/migrations/` ในเครื่อง** — ถ้า entrypoint เรียก `prisma migrate deploy` ตรง ๆ จะไม่มีอะไรเกิดขึ้นและตารางจะหายไปทั้งที่ process ขึ้นสำเร็จ จึงเลือกโหมดอัตโนมัติ:

| `SCHEMA_SYNC` | พฤติกรรม |
|---|---|
| `auto` (ค่าเริ่มต้น) | ถ้ามี `prisma/migrations/` → `migrate deploy`, ถ้าไม่มี → `db push` |
| `deploy` | บังคับ `prisma migrate deploy` |
| `push` | บังคับ `prisma db push` |
| `none` | ข้ามการ sync ทั้งหมด (เช่นเมื่อ release job apply schema แยก) |

ค่า `DATABASE_URL` เป็น required — ถ้าไม่ส่งมา container จะ exit ทันทีพร้อมข้อความบอก แทนที่จะพยายามต่อ DB แล้วล้มแบบกำกวม

`prisma` CLI ถูกย้ายจาก `devDependencies` ไป `dependencies` เพราะ entrypoint ต้องใช้ใน runtime — ตัว `@prisma/client` ที่แอป import ยังทำงานเหมือนเดิม

### Healthcheck

Image มี `HEALTHCHECK` ที่ยิง `/health` ด้วย `fetch` ของ Node 22 จึงไม่ต้องติดตั้ง `curl`/`wget` เพิ่มใน image

```bash
docker inspect --format '{{.State.Health.Status}}' <container>
```

## Seed data

```bash
cd server && npm run prisma:seed
```

`prisma/seed.ts` ใส่สินค้า **30 รายการ** ครอบคลุมทั้งสามสถานะ — `ACTIVE` 14, `DRAFT` 10, `ARCHIVED` 6

จำนวน 30 ตั้งใจเลือกให้เกิน `pageSize` default (20) พอดี จึงเห็น pagination 2 หน้าได้ทันทีโดยไม่ต้องแก้อะไร และมีคำให้ค้นหาหลากหลาย (ชื่อไทย, SKU, คำอธิบาย)

**Idempotent** — ใช้ `upsert` บน `sku` ที่ unique รันซ้ำกี่ครั้งก็ได้ ผลคือ update ไม่ใช่เพิ่มซ้ำ

หลังรันจะพิมพ์สรุป:

```
seeded 30 products (ACTIVE 14, DRAFT 10, ARCHIVED 6) - table now holds 30 rows
```

## Tests

```bash
cd server && npm test
```

ครอบ 3 ระดับ — pure helpers (pagination/where/order), Zod contract, และ HTTP contract ผ่าน supertest โดย mock service layer จึง **ไม่ต้องใช้ฐานข้อมูล**

```
Test Files  3 passed (3)
Tests       30 passed (30)
```

## Design notes

**ทำไมไม่ใช้ service layer ที่ inject เข้า controller** — controller เรียก service ผ่าน module import ตรง ๆ ทำให้ mock ด้วย `vi.mock` ได้ง่ายและไม่ต้องมี DI container

**ทำไม search state reset page** — ทุกครั้งที่คำค้นหรือ filter เปลี่ยน จะ reset `page` กลับเป็น 1 เพราะการอยู่หน้า 3 ขณะเปลี่ยนคำค้นมักได้ผลลัพธ์ว่าง

**ทำไม `placeholderData: keepPreviousData`** — แทนที่จะโชว์ loading เต็มจอทุกครั้งที่เปลี่ยนหน้า/ค้นหา ตารางจะคงข้อมูลหน้าเดิมไว้จนกว่าหน้าถัดไปจะโหลดเสร็จ (ดู dim ผ่าน `table-wrap--fetching`) UX จึงลื่นกว่า

**ทำไมแยก `useProductMutations`** — ตารางใช้ `remove` ส่วน modal ใช้ `create`/`update` ทั้งหมดใช้ invalidation logic ชุดเดียวกัน ถ้าแยกเขียนจะซ้ำและพลาด invalidation ได้ง่าย

**`price` เป็น `Decimal` ที่ฝั่ง DB** — service แปลงเป็น `number` ก่อนส่งออก และ Zod ฝั่ง server จำกัดทศนิยม 2 ตำแหน่ง ป้องกันการปัดเศษเงียบ ๆ

## Verification

- `server`: `npm run typecheck` ผ่าน (app + seed script, 0 errors), `npm run build` ผ่าน, `vitest run` → **30 passed**
- `web`: `tsc -b && vite build` ผ่าน → 98 modules, bundle 279.59 kB (gzip 85.46 kB)
