// backend/middleware/auth.js
const jwt = require("jsonwebtoken");

module.exports = function (req, res, next) {
  // ดึง token จาก header
  const token = req.header("Authorization")?.replace("Bearer ", "");

  if (!token) {
    return res.status(401).json({ message: "Access denied. No token provided." });
  }

  try {
    // ตรวจสอบ token ด้วย secret key
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded; // แนบข้อมูล user เข้าไปใน request
    next(); // ผ่านไปยัง route ถัดไป
  } catch (err) {
    res.status(400).json({ message: "Invalid token." });
  }
};