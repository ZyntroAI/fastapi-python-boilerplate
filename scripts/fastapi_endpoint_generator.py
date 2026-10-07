# ====================================================
# 🚀 FastAPI Endpoint Generator — สร้าง API อัตโนมัติ
# เวอร์ชัน: 1.0.0 | อัปเดต: 2026-10-08
# หน้าที่: สร้างโค้ด endpoint, schema, router แบบมาตรฐาน
# ====================================================

from __future__ import annotations

import re
from enum import Enum
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass, field


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


@dataclass
class EndpointField:
    """ข้อมูลฟิลด์ใน Request/Response"""
    name: str
    type: str = "str"
    required: bool = True
    description: str = ""
    example: Any = None


@dataclass
class EndpointConfig:
    """การกำหนดค่าแต่ละ Endpoint"""
    name: str
    path: str
    method: HTTPMethod
    description: str = ""
    summary: str = ""
    tags: List[str] = field(default_factory=list)
    request_fields: List[EndpointField] = field(default_factory=list)
    response_fields: List[EndpointField] = field(default_factory=list)
    include_auth: bool = False
    include_deprecated: bool = False
    response_model_name: str = ""


# ====================================================
# 🧩 แม่แบบโค้ด — Router
# ====================================================
ROUTER_TEMPLATE = '''"""
{module_name}.py — {module_title}
สร้างอัตโนมัติด้วย FastAPI Endpoint Generator
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

{auth_import}

router = APIRouter(
    prefix="{prefix}",
    tags={tags_list},
)

{schemas}

{endpoints}
'''

# ====================================================
# 🧩 แม่แบบ — Request/Response Schema
# ====================================================
SCHEMA_TEMPLATE = '''
class {schema_name}(BaseModel):
    """{schema_description}"""
{fields}
'''

# ====================================================
# 🧩 แม่แบบ — Endpoint Function
# ====================================================
ENDPOINT_TEMPLATE = '''
@router.{method_lower}(
    "{path}",
    status_code={status_code},
    summary="{summary}",
    description="""{description}""",
)
async def {function_name}(
{params}
) -> {response_model}:
    """
    {description}
    """
    {auth_dependency}
    
    try:
        # ==========================================
        # 🔘 TODO: เขียนตรรกะที่นี่
        # ==========================================
        raise NotImplementedError("Logic not implemented yet")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {{str(e)}}"
        )
'''


class FastAPIGenerator:
    """สร้างโค้ด FastAPI จากการกำหนดค่า"""

    TYPE_MAP = {
        "str": "str",
        "int": "int",
        "float": "float",
        "bool": "bool",
        "datetime": "datetime",
        "list[str]": "List[str]",
        "list[int]": "List[int]",
        "optional[str]": "Optional[str]",
    }

    STATUS_CODES = {
        "GET": 200,
        "POST": 201,
        "PUT": 200,
        "PATCH": 200,
        "DELETE": 204,
    }

    def __init__(self, module_name: str, prefix: str = "/api"):
        self.module_name = module_name
        self.prefix = prefix
        self.endpoints: List[EndpointConfig] = []

    def add_endpoint(self, config: EndpointConfig) -> "FastAPIGenerator":
        """เพิ่ม endpoint ที่จะสร้าง"""
        if not config.response_model_name:
            config.response_model_name = self._make_model_name(config.name, config.method)
        self.endpoints.append(config)
        return self

    def generate(self) -> str:
        """สร้างโค้ดทั้งหมดเป็นข้อความ"""
        schemas = []
        endpoints_code = []
        tags = set()
        has_auth = False

        for ep in self.endpoints:
            tags.update(ep.tags)
            if ep.include_auth:
                has_auth = True

            # สร้าง Schema
            if ep.request_fields:
                req_schema = self._build_schema(
                    name=self._make_model_name(ep.name, ep.method, "Request"),
                    description=f"Request สำหรับ {ep.name}",
                    fields=ep.request_fields,
                )
                schemas.append(req_schema)

            resp_schema = self._build_schema(
                name=ep.response_model_name,
                description=f"Response จาก {ep.name}",
                fields=ep.response_fields,
            )
            schemas.append(resp_schema)

            # สร้าง Endpoint
            endpoints_code.append(self._build_endpoint(ep))

        # รวมทั้งหมด
        return ROUTER_TEMPLATE.format(
            module_name=self.module_name,
            module_title=self.module_name.replace("_", " ").title(),
            prefix=self.prefix,
            tags_list=list(tags),
            schemas="\n".join(schemas),
            endpoints="\n".join(endpoints_code),
            auth_import="from app.dependencies import get_current_user\n" if has_auth else "",
        )

    def _make_model_name(self, name: str, method: HTTPMethod, suffix: str = "") -> str:
        """สร้างชื่อ Model แบบมาตรฐาน"""
        parts = re.sub(r"[-/]", " ", name).title().split()
        base = "".join(parts)
        return f"{base}{method.value}{suffix}"

    def _build_schema(self, name: str, description: str, fields: List[EndpointField]) -> str:
        """สร้างโค้ด Schema จากฟิลด์"""
        fields_code = []
        for f in fields:
            py_type = self.TYPE_MAP.get(f.type, f.type)
            default = "..." if f.required else "None"
            if f.description or f.example:
                fields_code.append(
                    f"    {f.name}: {py_type} = Field({default}, description={repr(f.description)}, example={repr(f.example)})"
                )
            else:
                fields_code.append(f"    {f.name}: {py_type} = {default}")

        return SCHEMA_TEMPLATE.format(
            schema_name=name,
            schema_description=description,
            fields="\n".join(fields_code),
        )

    def _build_endpoint(self, ep: EndpointConfig) -> str:
        """สร้างโค้ดฟังก์ชัน Endpoint"""
        method_lower = ep.method.value.lower()
        status_code = self.STATUS_CODES[ep.method.value]
        function_name = re.sub(r"[-/]", "_", ep.path.strip("/")).replace("{", "").replace("}", "")
        function_name = f"{method_lower}_{function_name}"

        # พารามิเตอร์
        params = []
        if ep.request_fields:
            req_model = self._make_model_name(ep.name, ep.method, "Request")
            params.append(f"    data: {req_model}")
        if ep.include_auth:
            params.append("    _ = Depends(get_current_user)")

        # Response model
        response_model = ep.response_model_name
        if ep.method == HTTPMethod.DELETE:
            response_model = "dict"

        return ENDPOINT_TEMPLATE.format(
            method_lower=method_lower,
            path=ep.path,
            status_code=status_code,
            summary=ep.summary or ep.name,
            description=ep.description,
            function_name=function_name,
            params=",\n".join(params) if params else "",
            response_model=response_model,
            auth_dependency="# ตรวจสิทธิ์ผู้ใช้" if ep.include_auth else "",
        )


# ====================================================
# 📌 ตัวอย่างการใช้งาน
# ====================================================
if __name__ == "__main__":
    generator = FastAPIGenerator(module_name="users", prefix="/v1/users")

    # === ตัวอย่าง: ดึงรายการผู้ใช้ ===
    generator.add_endpoint(EndpointConfig(
        name="list_users",
        path="/",
        method=HTTPMethod.GET,
        summary="ดึงรายการผู้ใช้",
        description="คืนรายการผู้ใช้ทั้งระบบ รองรับการแบ่งหน้า",
        tags=["Users"],
        response_fields=[
            EndpointField("total", "int", True, "จำนวนทั้งหมด", 123),
            EndpointField("page", "int", True, "หน้าปัจจุบัน", 1),
            EndpointField("items", "list[str]", True, "รายการผู้ใช้", ["id1", "id2"]),
        ],
        include_auth=True,
    ))

    # === ตัวอย่าง: สร้างผู้ใช้ ===
    generator.add_endpoint(EndpointConfig(
        name="create_user",
        path="/",
        method=HTTPMethod.POST,
        summary="สร้างผู้ใช้ใหม่",
        description="ลงทะเบียนผู้ใช้ด้วยอีเมลและรหัสผ่าน",
        tags=["Users"],
        request_fields=[
            EndpointField("email", "str", True, "ที่อยู่อีเมล", "user@example.com"),
            EndpointField("password", "str", True, "รหัสผ่าน อย่างน้อย 8 อักขระ", "********"),
            EndpointField("name", "str", False, "ชื่อที่แสดง", "ชื่อผู้ใช้"),
        ],
        response_fields=[
            EndpointField("id", "str", True, "รหัสผู้ใช้", "uuid-123"),
            EndpointField("email", "str", True, "อีเมล", "user@example.com"),
            EndpointField("created_at", "datetime", True, "เวลาที่สร้าง", "2026-10-08T04:00:00"),
        ],
    ))

    # === สร้างและบันทึก ===
    output = generator.generate()
    with open("users_router.py", "w", encoding="utf-8") as f:
        f.write(output)

    print("✅ สร้างไฟล์ users_router.py เรียบร้อยแล้ว!")
    print(output)
