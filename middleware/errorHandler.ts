การทำ Prisma error handling middleware จะช่วยให้ API ของคุณตอบกลับ error ได้อย่างสม่ำเสมอและอ่านง่าย โดยไม่ต้องเขียน try/catch ซ้ำ ๆ ในทุก endpoint  

---

🛠 ตัวอย่าง Middleware
`ts
// middleware/errorHandler.ts
import { Prisma } from "@prisma/client";
import { Request, Response, NextFunction } from "express";

export function errorHandler(
  err: any,
  req: Request,
  res: Response,
  next: NextFunction
) {
  console.error(err);

  // Prisma known errors
  if (err instanceof Prisma.PrismaClientKnownRequestError) {
    switch (err.code) {
      case "P2002": // Unique constraint failed
        return res.status(409).json({
          error: "Conflict",
          message: Duplicate field: ${err.meta?.target},
        });
      case "P2025": // Record not found
        return res.status(404).json({
          error: "Not Found",
          message: "Record does not exist",
        });
      default:
        return res.status(400).json({
          error: "Bad Request",
          message: Prisma error code: ${err.code},
        });
    }
  }

  // Prisma validation errors
  if (err instanceof Prisma.PrismaClientValidationError) {
    return res.status(400).json({
      error: "Validation Error",
      message: err.message,
    });
  }

  // Fallback
  return res.status(500).json({
    error: "Internal Server Error",
    message: "Unexpected error occurred",
  });
}
`

---

🔄 วิธีใช้ใน Express
`ts
import express from "express";
import { errorHandler } from "./middleware/errorHandler";

const app = express();

// ... routes เช่น /api/register, /api/products

// ใช้ errorHandler หลังสุด
app.use(errorHandler);
`

---

✅ ข้อดี
- Centralized error handling: ไม่ต้องเขียน try/catch ในทุก route  
- Readable HTTP responses: แปลง Prisma error code เป็น status + message ที่เข้าใจง่าย  
- Maintainability: เพิ่ม/แก้ไข mapping error ได้ในที่เดียว  

---

คุณอยากให้ผมช่วย เพิ่ม test case ด้วย Supertest ที่ยิง endpoint แล้วตรวจสอบว่า errorHandler ตอบกลับถูกต้อง (เช่น duplicate register → 409) เลยไหมครับ?
