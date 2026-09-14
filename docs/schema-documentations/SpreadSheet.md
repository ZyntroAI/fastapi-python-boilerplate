📊 Schema Documentation — Spreadsheet Version
 
สร้างชีตสรุป Schema ทั้งหมดในรูปแบบตารางที่จัดระเบียบและนำไปใช้งานได้ทันที ✅
 
 
 
📋 Sheet 1: Database Schema Summary
 
Table Name Column Name Data Type Constraints Default Description 
whatsapp_responses id SERIAL PRIMARY KEY AUTO Unique ID 
 user_number TEXT NOT NULL — WhatsApp user number 
 reply_id TEXT NOT NULL — Reply identifier 
 pr_number INT NULLABLE — Related PR number 
 timestamp TIMESTAMPTZ — NOW() Record time 
products id SERIAL PRIMARY KEY AUTO Product ID 
 sku VARCHAR(50) UNIQUE NOT NULL — Stock keeping unit 
 name VARCHAR(255) NOT NULL — Product name 
 description TEXT NULLABLE — Details 
 category VARCHAR(100) NULLABLE — Grouping 
 unit_price NUMERIC(12,2) NOT NULL 0 Price per unit 
 quantity INT NOT NULL CHECK ≥0 0 Stock quantity 
 reorder_level INT — 10 Reorder threshold 
 created_at TIMESTAMPTZ — NOW() Creation time 
 updated_at TIMESTAMPTZ — NOW() Last update 
inventory_transactions id SERIAL PRIMARY KEY AUTO Transaction ID 
 product_id INT FK → products(id) — Related product 
 quantity_change INT NOT NULL — +/- change amount 
 transaction_type VARCHAR(20) CHECK enum — STOCK_IN/SOLD/ADJUST/RETURN 
 notes TEXT NULLABLE — Comments 
 created_by TEXT NULLABLE — User/System 
 created_at TIMESTAMPTZ — NOW() Transaction time 
users id SERIAL PRIMARY KEY AUTO User ID 
 username VARCHAR(50) UNIQUE NOT NULL — Login name 
 email VARCHAR(255) UNIQUE NOT NULL — Contact 
 password_hash TEXT NOT NULL — Hashed password 
 display_name VARCHAR(100) NULLABLE — Public name 
 bio TEXT NULLABLE — Profile info 
 created_at TIMESTAMPTZ — NOW() Registration time 
 is_active BOOLEAN — TRUE Account status 
posts id SERIAL PRIMARY KEY AUTO Post ID 
 author_id INT FK → users(id) — Writer reference 
 title VARCHAR(200) NOT NULL — Post title 
 slug VARCHAR(200) UNIQUE NOT NULL — URL identifier 
 content TEXT NOT NULL — Body content 
 status VARCHAR(20) CHECK enum DRAFT DRAFT/PUBLISHED/ARCHIVED 
 published_at TIMESTAMPTZ NULLABLE — Go-live time 
 created_at TIMESTAMPTZ — NOW() Creation time 
 updated_at TIMESTAMPTZ — NOW() Last edit 
 
 
 
📋 Sheet 2: Prisma Model Summary
 
Model Name Field Name Type Attributes DB Column Name 
WhatsappResponse id Int @id @default(autoincrement()) id 
 userNumber String  user_number 
 replyId String  reply_id 
 prNumber Int?  pr_number 
 timestamp DateTime @default(now()) @db.Timestamptz() timestamp 
Product id Int @id @default(autoincrement()) id 
 sku String @unique sku 
 name String  name 
 description String?  description 
 category String?  category 
 unitPrice Decimal  unit_price 
 quantity Int @default(0) quantity 
 reorderLevel Int @default(10) reorder_level 
 createdAt DateTime @default(now()) created_at 
 updatedAt DateTime @updatedAt updated_at 
User id Int @id @default(autoincrement()) id 
 username String @unique username 
 email String @unique email 
 passwordHash String  password_hash 
 displayName String?  display_name 
 bio String?  bio 
 createdAt DateTime @default(now()) created_at 
 isActive Boolean @default(true) is_active 
Post id Int @id @default(autoincrement()) id 
 authorId Int  author_id 
 title String  title 
 slug String @unique slug 
 content String  content 
 status String @default("DRAFT") status 
 publishedAt DateTime?  published_at 
 createdAt DateTime @default(now()) created_at 
 updatedAt DateTime @updatedAt updated_at 
 
 
 
📋 Sheet 3: API Endpoint Summary
 
Method Path Summary Query Params Request Body Response 
GET  /posts  List all posts status, page, limit — { data: Post[], total, page } 
POST  /posts  Create post — { title, slug?, content, status? } Post (201) 
GET  /products  List products — — Product[] 
 
Schema Objects
 
Name Fields Required Validation 
Post id, title, slug, content, status, authorId, publishedAt, createdAt All status: DRAFT/PUBLISHED/ARCHIVED 
PostCreate title, slug, content, status title, content title: 3–200 chars 
Product id, sku, name, unitPrice, quantity, reorderLevel All Numeric fields ≥0 
 
 
 
📋 Sheet 4: Helm / Values Schema Summary
 
Key Purpose Example Notes 
 global.env.LOG_LEVEL  Log verbosity info debug/info/warn/error 
 api.replicaCount  Pod replicas 2 Horizontal scaling 
 api.service.port  API port 8080 Container port 
 skipPayment.cron.schedule  Job timing "0 0 * * *" Daily midnight 
 postgres.auth.database  DB name payments — 
 postgres.primary.persistence.size  Storage 8Gi Volume capacity 
 *.env.*.valueFrom.secretKeyRef  Secure values payments-db-secret ✅ Secrets NOT hardcoded 
 
 
 
✅ Validation Checklist
 
# Rule Status 
1 All tables have primary key + timestamps ✅ 
2 Foreign keys with ON DELETE CASCADE ✅ 
3 Unique constraints on sku, slug, username, email ✅ 
4 CHECK/enum constraints for status & types ✅ 
5 Secrets via secretKeyRef only ✅ 
6 Prisma snake_case ↔ camelCase mapped ✅ 
7 OpenAPI types & validation defined ✅ 
8 Decimal precision for currency ✅ 
 
 
 
📥 How to Use in Excel / Google Sheets
 
1. Copy entire table by table → Paste directly into Excel
2. Auto-filter columns → Sort/filter easily
3. Format as Table → banded rows, filters enabled
 
ต้องการให้ส่งออกเป็นไฟล์ .csv แยกชีต หรือสร้างเป็น Google Sheets ที่แชร์ได้เลยไหมครับ? 😊
