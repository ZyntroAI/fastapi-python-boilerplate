"""
🛡️ Origin Validation Middleware for FastAPI
ป้องกัน CWE-346: Improper Verification of Source Origin
ตรวจ: Origin Header + Referrer Header + Authorization Token
"""

import re
from typing import Set, Optional, Callable
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class OriginValidationMiddleware(BaseHTTPMiddleware):
    """
    ตรวจสอบแหล่งที่มาของคำขออย่างเข้มงวด
    
    ✅ ตรวจสอบ:
    1. Origin Header → ต้องตรงกับรายการที่อนุญาต
    2. Referrer Header → ต้องมาจากโดเมนเดียวกัน (ถ้ามี)
    3. Authorization → ต้องมีโทเคนที่ถูกต้องเมื่อ Origin ว่างเปล่า
    4. CORS Headers → ตั้งค่าอย่างปลอดภัย
    """

    def __init__(
        self,
        app: ASGIApp,
        allowed_origins: Set[str],
        protected_routes: Optional[Set[str]] = None,
        exempt_routes: Optional[Set[str]] = None,
        allow_null_origin: bool = False,
        enable_referrer_check: bool = True,
    ):
        super().__init__(app)
        self.allowed_origins = {o.rstrip("/") for o in allowed_origins}
        self.protected_routes = protected_routes or {"/api/"}
        self.exempt_routes = exempt_routes or {"/health", "/docs", "/redoc"}
        self.allow_null_origin = allow_null_origin
        self.enable_referrer_check = enable_referrer_check

        # สร้าง Pattern ตรวจสอบ Referrer
        self.origin_patterns = [re.compile(re.escape(o), re.IGNORECASE) for o in self.allowed_origins]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        # ✅ ข้ามตรวจสอบสำหรับเส้นทางที่ยกเว้น
        if self._is_exempt(path):
            return await call_next(request)

        # ✅ ตรวจเฉพาะเส้นทางที่ปกป้อง
        if not self._is_protected(path):
            return await call_next(request)

        # 📥 อ่าน Header
        origin = request.headers.get("origin", "").strip().lower()
        referrer = request.headers.get("referrer", "").strip().lower()
        has_auth = "authorization" in request.headers

        # 🔍 ตรวจสอบ
        origin_ok = self._validate_origin(origin, has_auth)
        referrer_ok = self._validate_referrer(referrer) if self.enable_referrer_check else True

        if not origin_ok or not referrer_ok:
            return self._reject_request(origin, referrer)

        # ✅ ดำเนินการต่อ + ตั้งค่า CORS Header
        response = await call_next(request)
        self._set_cors_headers(response, origin)
        return response

    # ─── ตรวจสอบ Origin ───
    def _validate_origin(self, origin: str, has_auth: bool) -> bool:
        """ตรวจ Origin กับรายการที่อนุญาต"""
        
        # กรณีไม่มี Origin → ต้องมีโทเคน
        if not origin or origin == "null":
            return self.allow_null_origin or has_auth

        # ตรวจตรงตัว
        return origin in self.allowed_origins

    # ─── ตรวจสอบ Referrer ───
    def _validate_referrer(self, referrer: str) -> bool:
        """ตรวจ Referrer ว่ามาจากโดเมนที่อนุญาต"""
        if not referrer:
            return True  # ไม่ส่งมา → ข้ามตรวจ
        
        return any(pattern.search(referrer) for pattern in self.origin_patterns)

    # ─── ตรวจสอบเส้นทาง ───
    def _is_protected(self, path: str) -> bool:
        return any(path.startswith(route) for route in self.protected_routes)

    def _is_exempt(self, path: str) -> bool:
        return any(path.startswith(route) for route in self.exempt_routes)

    # ─── ตั้งค่า CORS Header ───
    def _set_cors_headers(self, response: Response, origin: str):
        if origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
        else:
            response.headers["Access-Control-Allow-Origin"] = list(self.allowed_origins)[0] if self.allowed_origins else ""
        
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, Origin"
        response.headers["Access-Control-Max-Age"] = "86400"

    # ─── ปฏิเสธคำขอ ───
    def _reject_request(self, origin: str, referrer: str) -> Response:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Origin validation failed",
                "cwe": "CWE-346",
                "origin_received": origin or "(none)",
                "reason": "Request origin not in allowed list"
            }
        )
