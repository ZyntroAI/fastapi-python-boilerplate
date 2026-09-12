# Fig Google Drive Upload Test

ทดสอบการอัปโหลดไฟล์จาก workspace ขึ้น Google Drive ผ่าน connector

| รายการ | ค่า |
|---|---|
| วันที่ทดสอบ | 2026-09-10 |
| บัญชีปลายทาง | zyntro.ai.studio@gmail.com |
| โฟลเดอร์ปลายทาง | Fig Connector Test 2026-09-10 |
| ไฟล์ต้นทาง | workspace (sandbox) |

## ขั้นตอนที่ทดสอบ

1. สร้างไฟล์นี้ใน workspace
2. อัปโหลดขึ้น Drive พร้อมระบุ `parents` เป็น folder id
3. Query กลับเพื่อยืนยันว่าไฟล์อยู่ในโฟลเดอร์จริง

## หมายเหตุ

- ไฟล์นี้เป็นไฟล์ทดสอบ ไม่มีข้อมูลสำคัญ
- ถ้าไม่ต้องการแล้ว ให้ trash ได้ทันที
