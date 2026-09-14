/**
 * Seed data for local development and UI checks.
 *
 * 30 products across all three statuses, enough to exercise pagination
 * (30 rows = 2 pages at the default pageSize of 20) and to give the search
 * box something meaningful to match against.
 *
 * Idempotent: rows are upserted on the unique `sku`, so running it twice
 * updates instead of duplicating.
 *
 *   npx prisma db seed        # or: npm run prisma:seed
 */
import { PrismaClient, ProductStatus } from "@prisma/client";

const prisma = new PrismaClient();

interface SeedProduct {
  name: string;
  sku: string;
  description: string | null;
  price: number;
  stock: number;
  status: ProductStatus;
}

const PRODUCTS: SeedProduct[] = [
  // ---- ACTIVE (14) — the bulk of a working catalogue
  { name: "ประแจทอร์ก 1/2 นิ้ว", sku: "TW-100", description: "แรงบิด 20-100 ft-lb พร้อมกระเป๋า", price: 2450, stock: 12, status: ProductStatus.ACTIVE },
  { name: "ชุดดอกสว่าน HSS 19 ชิ้น", sku: "DR-019", description: "เคลือบไทเทเนียม สำหรับเหล็กและไม้", price: 890.5, stock: 34, status: ProductStatus.ACTIVE },
  { name: "คีมล็อกปากตรง 10 นิ้ว", sku: "VL-010", description: "ปากแข็งพิเศษ จับแน่นไม่ลื่น", price: 320, stock: 48, status: ProductStatus.ACTIVE },
  { name: "ตลับเมตร 5 เมตร", sku: "MT-005", description: "แถบเหล็กชุบ สกรูหยุดอัตโนมัติ", price: 149, stock: 120, status: ProductStatus.ACTIVE },
  { name: "ไขควงชุด 12 ชิ้น", sku: "SD-012", description: "ด้ามยางกันลื่น ปลายแม่เหล็ก", price: 590, stock: 60, status: ProductStatus.ACTIVE },
  { name: "ค้อนหัวกลม 16 oz", sku: "HM-016", description: "ด้ามไฟเบอร์กลาส ลดแรงสะเทือน", price: 410, stock: 25, status: ProductStatus.ACTIVE },
  { name: "เลื่อยฉลุ 8 นิ้ว", sku: "HW-008", description: "ใบเลื่อย 8 TPI สำหรับไม้และ PVC", price: 275, stock: 40, status: ProductStatus.ACTIVE },
  { name: "ชุดประแจแหวน 8-24 mm", sku: "WR-024", description: "12 ขนาด บรรจุในม้วนผ้าใบ", price: 1890, stock: 8, status: ProductStatus.ACTIVE },
  { name: "สว่านไร้สาย 18V", sku: "CD-018", description: "แบตเตอรี่ลิเธียม 2 ก้อน + กระเป๋า", price: 5490, stock: 6, status: ProductStatus.ACTIVE },
  { name: "คีมตัดลวด 7 นิ้ว", sku: "WC-007", description: "ตัดลวดเหล็กได้ถึง 2 mm", price: 380, stock: 52, status: ProductStatus.ACTIVE },
  { name: "ระดับน้ำอลูมิเนียม 60 cm", sku: "LV-060", description: "แม่เหล็ก 3 จุด กันกระแทก", price: 720, stock: 18, status: ProductStatus.ACTIVE },
  { name: "ประแจเลื่อน 12 นิ้ว", sku: "AW-012", description: "ปากปรับได้ 0-34 mm", price: 465, stock: 30, status: ProductStatus.ACTIVE },
  { name: "ชุดบล็อก 40 ชิ้น", sku: "SK-040", description: "BLK 1/4 + 3/8 พร้อมก้านต่อ", price: 3100, stock: 9, status: ProductStatus.ACTIVE },
  { name: "แว่นตากันเศษ ใส", sku: "SG-001", description: "ผ่านมาตรฐาน ANSI Z87.1", price: 165, stock: 200, status: ProductStatus.ACTIVE },

  // ---- DRAFT (10) — staged but not yet sellable
  { name: "กล่องเครื่องมือล้อเลื่อน 22 นิ้ว", sku: "TB-220", description: "ตัวถัง ABS ล้อ PU รับน้ำหนัก 40 kg", price: 3190, stock: 5, status: ProductStatus.DRAFT },
  { name: "เครื่องอัดจาระบีมือ 500 cc", sku: "GG-500", description: "แรงดันสูง พร้อมหัวต่อ", price: 1450, stock: 0, status: ProductStatus.DRAFT },
  { name: "ชุดหัวแร้งบัดกรี 60W", sku: "SL-060", description: "ปรับอุณหภูมิ 200-450 องศา", price: 980, stock: 14, status: ProductStatus.DRAFT },
  { name: "คีมย้ำหางปลา 6 ขนาด", sku: "CT-006", description: "ด้ามไฟเบอร์กลาส ไม่ลื่น", price: 520, stock: 22, status: ProductStatus.DRAFT },
  { name: "ไฟฉายคาดหัว LED 350 lm", sku: "HL-350", description: "ชาร์จ USB-C สว่าง 3 โหมด", price: 690, stock: 37, status: ProductStatus.DRAFT },
  { name: "ชุดต๊าปเกลียว M3-M12", sku: "TP-M12", description: "ไทเทเนียม 2 ตี ครบชุด", price: 4700, stock: 3, status: ProductStatus.DRAFT },
  { name: "สายวัดเลเซอร์ 40 m", sku: "LM-040", description: "ความคลาดเคลื่อน +/- 2 mm", price: 4850, stock: 4, status: ProductStatus.DRAFT },
  { name: "ชุดคีมถอดพิน 4 ชิ้น", sku: "PP-004", description: "ปลายแหลมและปลายงอ ขนาด 1.5-3 mm", price: 340, stock: 26, status: ProductStatus.DRAFT },
  { name: "เครื่องเจียร์มุม 125 mm", sku: "AG-125", description: "1,100W ความเร็ว 11,000 rpm", price: 3290, stock: 7, status: ProductStatus.DRAFT },
  { name: "ถุงมือกันบาด ระดับ 5", sku: "GL-L5", description: "ไฟเบอร์ HPPE น้ำหนักเบา ระบายอากาศ", price: 245, stock: 0, status: ProductStatus.DRAFT },

  // ---- ARCHIVED (6) — discontinued, still visible for old orders
  { name: "คีมล็อก 10 นิ้ว (รุ่นเก่า)", sku: "VL-010-OLD", description: "สินค้าเลิกผลิต แทนด้วย VL-010", price: 320, stock: 0, status: ProductStatus.ARCHIVED },
  { name: "ไขควงไฟฟ้า 3.6V (รุ่นเก่า)", sku: "ED-036-OLD", description: "สินค้าเลิกผลิต แทนด้วย CD-018", price: 1290, stock: 0, status: ProductStatus.ARCHIVED },
  { name: "ชุดบล็อก 24 ชิ้น (รุ่นเก่า)", sku: "SK-024-OLD", description: "สินค้าเลิกผลิต แทนด้วย SK-040", price: 1750, stock: 0, status: ProductStatus.ARCHIVED },
  { name: "ตลับเมตร 3 เมตร (รุ่นเก่า)", sku: "MT-003-OLD", description: "สินค้าเลิกผลิต แทนด้วย MT-005", price: 95, stock: 0, status: ProductStatus.ARCHIVED },
  { name: "ค้อนหงอน 16 oz (รุ่นเก่า)", sku: "HM-016-OLD", description: "สินค้าเลิกผลิต ด้ามไม้", price: 260, stock: 0, status: ProductStatus.ARCHIVED },
  { name: "แว่นตากันเศษ (รุ่นเก่า)", sku: "SG-001-OLD", description: "สินค้าเลิกผลิต แทนด้วย SG-001", price: 120, stock: 0, status: ProductStatus.ARCHIVED },
];

async function main() {
  const counts = { ACTIVE: 0, DRAFT: 0, ARCHIVED: 0 };

  for (const product of PRODUCTS) {
    await prisma.product.upsert({
      where: { sku: product.sku },
      update: {
        name: product.name,
        description: product.description,
        price: product.price,
        stock: product.stock,
        status: product.status,
      },
      create: product,
    });
    counts[product.status] += 1;
  }

  const total = await prisma.product.count();
  console.log(
    `seeded ${PRODUCTS.length} products ` +
      `(ACTIVE ${counts.ACTIVE}, DRAFT ${counts.DRAFT}, ARCHIVED ${counts.ARCHIVED}) - ` +
      `table now holds ${total} rows`,
  );
}

main()
  .catch((error) => {
    console.error("seed failed:", error);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
