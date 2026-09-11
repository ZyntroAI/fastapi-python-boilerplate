# product-crud — Products CRUD (Prisma + Express + React)

ชุด deliverable แบบ self-contained สำหรับงาน CRUD สินค้า — backend (Express + Prisma + Zod) และ frontend (React + TanStack Query + React Hook Form) ใช้ **Zod schema เดียวกัน** ทั้งสองฝั่ง จึงไม่ต้อง sync type ด้วยมือ

## โครงสร้าง

```
product-crud/
├── server/                        # Express + Prisma + Zod
│   ├── prisma/schema.prisma       # Product model + ProductStatus enum + indexes
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

## Setup

```bash
# 1) ฐานข้อมูล — ต้องมี Postgres ก่อน
cd server
cp .env.example .env          # ตั้ง DATABASE_URL
npm install
npm run prisma:generate
npm run prisma:migrate        # สร้างตาราง products

# 2) รัน API
npm run dev                   # http://localhost:4000

# 3) รัน frontend (คนละ terminal)
cd ../web
cp .env.example .env          # VITE_API_BASE_URL=http://localhost:4000
npm install
npm run dev                   # http://localhost:5173
```

Vite ตั้ง proxy `/api` ไปที่ `http://localhost:4000` ไว้ให้แล้ว ถ้าไม่ตั้ง `VITE_API_BASE_URL` ก็ยังเรียก API ผ่าน proxy ได้

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

- `server`: `tsc --noEmit` ผ่าน (0 errors), `vitest run` → **30 passed**
- `web`: `tsc -b && vite build` ผ่าน → 98 modules, bundle 279.59 kB (gzip 85.46 kB)
