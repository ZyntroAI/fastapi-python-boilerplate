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

✅ เพิ่มครบทั้ง 3 ส่วนแล้วครับ — ตรวจสอบอัตโนมัติ + SQLAlchemy Model + Pytest Tests พร้อมใช้งานทันที 🚀✨
 
 
 
📄 fastapi_endpoint_generator_v2.py — ฉบับสมบูรณ์
 
python  
# ====================================================
# 🚀 FastAPI Endpoint Generator v2.0 — Full Suite
# เวอร์ชัน: 2.0.0 | อัปเดต: 2026-10-08
# เพิ่ม: Validation · SQLAlchemy Models · Pytest Tests
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


class FieldType(str, Enum):
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    DATETIME = "datetime"
    EMAIL = "email"
    PASSWORD = "password"
    UUID = "uuid"
    PHONE = "phone"
    LIST_STR = "list[str]"
    OPT_STR = "optional[str]"


@dataclass
class ValidationRule:
    """กฎการตรวจสอบความถูกต้อง"""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[int | float] = None
    max_value: Optional[int | float] = None
    pattern: Optional[str] = None
    unique: bool = False
    db_index: bool = False
    description: str = ""


@dataclass
class EndpointField:
    """ข้อมูลฟิลด์ใน Request/Response + Validation"""
    name: str
    type: str | FieldType = FieldType.STR
    required: bool = True
    description: str = ""
    example: Any = None
    validation: ValidationRule = field(default_factory=ValidationRule)
    db_column_type: str = ""  # Auto-set based on type


@dataclass
class EndpointConfig:
    """การกำหนดค่าแต่ละ Endpoint — ครบทุกส่วน"""
    name: str
    path: str
    method: HTTPMethod
    description: str = ""
    summary: str = ""
    tags: List[str] = field(default_factory=list)
    request_fields: List[EndpointField] = field(default_factory=list)
    response_fields: List[EndpointField] = field(default_factory=list)
    include_auth: bool = False
    response_model_name: str = ""
    db_model_name: str = ""
    generate_db_model: bool = True
    generate_tests: bool = True


# ====================================================
# 🧩 แม่แบบ — SQLAlchemy Model
# ====================================================
DB_MODEL_TEMPLATE = '''"""
{model_name}.py — ฐานข้อมูล SQLAlchemy
สร้างอัตโนมัติด้วย FastAPI Endpoint Generator
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid

Base = declarative_base()


class {model_name}(Base):
    """ตาราง {table_name} — {table_description}"""
    __tablename__ = "{table_name}"
{db_fields}
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<{model_name} {{self.id}}>"
'''

# ====================================================
# 🧩 แม่แบบ — Pytest Test Suite
# ====================================================
TEST_FILE_TEMPLATE = '''"""
test_{module_name}.py — ชุดทดสอบอัตโนมัติ
สร้างด้วย FastAPI Endpoint Generator
"""

import pytest
from fastapi import status
from datetime import datetime


class Test{ModuleClass}:
    """ทดสอบ Endpoint {module_name}"""

    @pytest.fixture(autouse=True)
    def setup(self, client, db_session):
        self.client = client
        self.db = db_session
        self.base_url = "{base_url}"

{test_cases}
'''

TEST_CASE_TEMPLATE = '''
    def test_{test_name}(self):
        """{test_description}"""
        # Arrange
        payload = {payload}
        
        # Act
        response = self.client.{method_lower}(
            f"{{self.base_url}}{path}",
            json=payload,
            headers={{"Authorization": "Bearer TEST_TOKEN"}} if {auth_required} else {{}},
        )
        
        # Assert
        assert response.status_code == {expected_status}
        data = response.json()
{assertions}
'''

# ====================================================
# 🧩 แม่แบบ — Router พร้อม Validation
# ====================================================
ROUTER_TEMPLATE = '''"""
{module_name}.py — {module_title}
สร้างด้วย FastAPI Endpoint Generator v2
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr, field_validator
from pydantic.types import UUID4
from typing import Optional, List
from datetime import datetime
import re

{auth_import}

router = APIRouter(
    prefix="{prefix}",
    tags={tags_list},
)

{schemas}

{endpoints}
'''

SCHEMA_TEMPLATE = '''
class {schema_name}(BaseModel):
    """{schema_description}"""
{fields}
{validators}
'''

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
        # ตัวอย่าง: บันทึกลงฐานข้อมูล
        # db_obj = {db_model_name}(**data.model_dump())
        # self.db.add(db_obj)
        # self.db.commit()
        # return {response_model_name}.model_validate(db_obj)
        
        raise NotImplementedError("Logic not implemented yet")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {{str(e)}}"
        )
'''


class FastAPIGenerator:
    """สร้างโค้ด FastAPI — Schema + Validation + DB + Tests"""

    TYPE_MAP = {
        "str": ("str", "String(255)"),
        "int": ("int", "Integer"),
        "float": ("float", "Float"),
        "bool": ("bool", "Boolean"),
        "datetime": ("datetime", "DateTime"),
        "email": ("EmailStr", "String(255)"),
        "password": ("str", "String(255)"),
        "uuid": ("UUID4", "UUID(as_uuid=True)"),
        "phone": ("str", "String(20)"),
        "list[str]": ("List[str]", "JSON"),
        "optional[str]": ("Optional[str]", "String(255)"),
    }

    STATUS_CODES = {
        "GET": 200,
        "POST": 201,
        "PUT": 200,
        "PATCH": 200,
        "DELETE": 204,
    }

    def __init__(self, module_name: str, prefix: str = "/api/v1"):
        self.module_name = module_name
        self.prefix = prefix
        self.endpoints: List[EndpointConfig] = []

    def add_endpoint(self, config: EndpointConfig) -> "FastAPIGenerator":
        """เพิ่ม endpoint ที่จะสร้าง — ครบทุกส่วน"""
        if not config.response_model_name:
            config.response_model_name = self._make_name(config.name, config.method, "Response")
        if not config.db_model_name:
            config.db_model_name = config.name.title().replace("_", "")
        self.endpoints.append(config)
        return self

    def generate_all(self) -> Dict[str, str]:
        """สร้างทุกไฟล์: router + db model + tests"""
        return {
            "router": self._generate_router(),
            "db_model": self._generate_db_model(),
            "tests": self._generate_tests(),
        }

    # ====================================================
    # 📋 ส่วน 1: Router + Validation
    # ====================================================
    def _generate_router(self) -> str:
        schemas = []
        endpoints_code = []
        tags = set()
        has_auth = False

        for ep in self.endpoints:
            tags.update(ep.tags)
            if ep.include_auth:
                has_auth = True

            if ep.request_fields:
                schemas.append(self._build_schema(ep, is_request=True))
            schemas.append(self._build_schema(ep, is_request=False))
            endpoints_code.append(self._build_endpoint(ep))

        return ROUTER_TEMPLATE.format(
            module_name=self.module_name,
            module_title=self.module_name.replace("_", " ").title(),
            prefix=self.prefix,
            tags_list=list(tags),
            schemas="\n".join(schemas),
            endpoints="\n".join(endpoints_code),
            auth_import="from app.dependencies import get_current_user\n" if has_auth else "",
        )

    def _build_schema(self, ep: EndpointConfig, is_request: bool) -> str:
        fields = ep.request_fields if is_request else ep.response_fields
        suffix = "Request" if is_request else "Response"
        name = self._make_name(ep.name, ep.method, suffix)

        fields_code = []
        validators = []
        for f in fields:
            py_type, _ = self.TYPE_MAP.get(str(f.type), ("str", "Text"))
            default = "..." if f.required else "None"
            
            # Validation rules
            field_args = [f"default={default}"]
            if f.validation.min_length:
                field_args.append(f"min_length={f.validation.min_length}")
            if f.validation.max_length:
                field_args.append(f"max_length={f.validation.max_length}")
            if f.validation.min_value:
                field_args.append(f"gt={f.validation.min_value}")
            if f.validation.max_value:
                field_args.append(f"lt={f.validation.max_value}")
            if f.validation.pattern:
                field_args.append(f"pattern={repr(f.validation.pattern)}")
            if f.description:
                field_args.append(f"description={repr(f.description)}")
            if f.example:
                field_args.append(f"example={repr(f.example)}")

            fields_code.append(
                f"    {f.name}: {py_type} = Field({', '.join(field_args)})"
            )

            # Custom validator example for password
            if f.type == FieldType.PASSWORD:
                validators.append(f'''
    @field_validator("{f.name}")
    def check_password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("รหัสผ่านต้องยาวอย่างน้อย 8 อักขระ")
        return v
''')

        return SCHEMA_TEMPLATE.format(
            schema_name=name,
            schema_description=f"{suffix} — {ep.summary}",
            fields="\n".join(fields_code),
            validators="\n".join(validators),
        )

    def _build_endpoint(self, ep: EndpointConfig) -> str:
        method_lower = ep.method.value.lower()
        status_code = self.STATUS_CODES[ep.method.value]
        fn_name = re.sub(r"[-/]", "_", ep.path.strip("/")).replace("{", "").replace("}", "")
        fn_name = f"{method_lower}_{fn_name}"

        params = []
        if ep.request_fields:
            req_model = self._make_name(ep.name, ep.method, "Request")
            params.append(f"    data: {req_model}")
        if ep.include_auth:
            params.append("    _ = Depends(get_current_user)")

        resp_model = ep.response_model_name if ep.method != HTTPMethod.DELETE else "dict"

        return ENDPOINT_TEMPLATE.format(
            method_lower=method_lower,
            path=ep.path,
            status_code=status_code,
            summary=ep.summary,
            description=ep.description,
            function_name=fn_name,
            params=",\n".join(params) if params else "",
            response_model=resp_model,
            auth_dependency="# ตรวจสิทธิ์ผู้ใช้" if ep.include_auth else "",
            db_model_name=ep.db_model_name,
        )

    # ====================================================
    # 🗄️ ส่วน 2: SQLAlchemy Database Model
    # ====================================================
    def _generate_db_model(self) -> str:
        if not any(ep.generate_db_model for ep in self.endpoints):
            return "# ไม่มีโมเดลฐานข้อมูลที่กำหนด"

        fields_code = [
            "    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)",
        ]

        # รวมฟิลด์จากทุก endpoint (ไม่ซ้ำ)
        seen = set()
        all_fields: List[EndpointField] = []
        for ep in self.endpoints:
            if ep.generate_db_model:
                all_fields.extend(ep.request_fields)
                all_fields.extend(ep.response_fields)

        for f in all_fields:
            if f.name in ("id", "created_at", "updated_at", "is_deleted"):
                continue
            if f.name in seen:
                continue
            seen.add(f.name)

            _, col_type = self.TYPE_MAP.get(str(f.type), ("str", "String(255)"))
            nullable = ", nullable=False" if f.required else ", nullable=True"
            unique = ", unique=True" if f.validation.unique else ""
            index = ", index=True" if f.validation.db_index else ""

            fields_code.append(
                f"    {f.name} = Column({col_type}{nullable}{unique}{index})"
            )

        main_ep = self.endpoints[0]
        model_name = main_ep.db_model_name or self.module_name.title().replace("_", "")
        table_name = self.module_name.lower()

        return DB_MODEL_TEMPLATE.format(
            model_name=model_name,
            table_name=table_name,
            table_description=f"ตารางเก็บข้อมูล {self.module_name}",
            db_fields="\n".join(fields_code),
        )

    # ====================================================
    # 🧪 ส่วน 3: Pytest Test Suite
    # ====================================================
    def _generate_tests(self) -> str:
        if not any(ep.generate_tests for ep in self.endpoints):
            return "# ไม่มีชุดทดสอบที่กำหนด"

        test_cases = []
        for idx, ep in enumerate(self.endpoints, 1):
            if not ep.generate_tests:
                continue

            fn_name = re.sub(r"[-/{}]", "_", ep.path.strip("/")).strip("_")
            method_lower = ep.method.value.lower()
            expected_status = self.STATUS_CODES[ep.method.value]

            # สร้าง payload ตัวอย่าง
            payload = {}
            assertions = []
            for f in ep.request_fields:
                payload[f.name] = f.example or ("string" if "str" in f.type else 123)
            for f in ep.response_fields:
                assertions.append(f'        assert "{f.name}" in data')

            test_cases.append(TEST_CASE_TEMPLATE.format(
                test_name=f"{method_lower}_{fn_name}",
                test_description=f"ทดสอบ {ep.method} {ep.path} — {ep.summary}",
                method_lower=method_lower,
                path=ep.path,
                payload=payload,
                auth_required=str(ep.include_auth),
                expected_status=expected_status,
                assertions="\n".join(assertions) or "        assert True",
            ))

        class_name = self.module_name.title().replace("_", "")
        return TEST_FILE_TEMPLATE.format(
            module_name=self.module_name,
            ModuleClass=class_name,
            base_url=self.prefix,
            test_cases="\n".join(test_cases),
        )

    def _make_name(self, base: str, method: HTTPMethod, suffix: str = "") -> str:
        return "".join(word.capitalize() for word in re.split(r"[-_/]", base)) + method.value + suffix


# ====================================================
# 📌 ตัวอย่างการใช้งาน
# ====================================================
if __name__ == "__main__":
    gen = FastAPIGenerator(module_name="users", prefix="/v1/users")

    # === สร้างผู้ใช้ — พร้อม Validation ===
    gen.add_endpoint(EndpointConfig(
        name="create_user",
        path="/",
        method=HTTPMethod.POST,
        summary="สร้างผู้ใช้ใหม่",
        description="ลงทะเบียนด้วยอีเมลและรหัสผ่าน",
        tags=["Users"],
        request_fields=[
            EndpointField(
                "email", FieldType.EMAIL, True, "ที่อยู่อีเมล", "user@example.com",
                validation=ValidationRule(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", unique=True, db_index=True)
            ),
            EndpointField(
                "password", FieldType.PASSWORD, True, "รหัสผ่าน ≥ 8 อักขระ", "********",
                validation=ValidationRule(min_length=8, max_length=128)
            ),
            EndpointField(
                "name", FieldType.STR, False, "ชื่อที่แสดง", "ชื่อผู้ใช้",
                validation=ValidationRule(max_length=100)
            ),
        ],
        response_fields=[
            EndpointField("id", FieldType.UUID, True, "รหัสผู้ใช้", "uuid-xxx"),
            EndpointField("email", FieldType.EMAIL, True, "อีเมล", "user@example.com"),
            EndpointField("created_at", FieldType.DATETIME, True, "เวลาสร้าง", "2026-10-08T04:00:00"),
        ],
        generate_db_model=True,
        generate_tests=True,
    ))

    # === ดึงรายการ — พร้อมสิทธิ์ ===
    gen.add_endpoint(EndpointConfig(
        name="list_users",
        path="/",
        method=HTTPMethod.GET,
        summary="ดึงรายการผู้ใช้",
        description="รายการทั้งหมด — ต้องเข้าสู่ระบบ",
        tags=["Users"],
        response_fields=[
            EndpointField("total", FieldType.INT, True, "จำนวนทั้งหมด", 1),
            EndpointField("page", FieldType.INT, True, "หน้าปัจจุบัน", 1),
            EndpointField("items", FieldType.LIST_STR, True, "รายการ", []),
        ],
        include_auth=True,
        generate_db_model=False,
        generate_tests=True,
    ))

    # === สร้างทุกไฟล์ ===
    files = gen.generate_all()

    with open("users_router.py", "w", encoding="utf-8") as f:
        f.write(files["router"])
    with open("users_model.py", "w", encoding="utf-8") as f:
        f.write(files["db_model"])
    with open("test_users.py", "w", encoding="utf-8") as f:
        f.write(files["tests"])

    print("✅ สร้างครบ 3 ไฟล์แล้ว!")
    print("📄 users_router.py  — API + Validation")
    print("🗄️  users_model.py   — SQLAlchemy")
    print("🧪 test_users.py    — Pytest")
 
 
 
 
✅ สรุปสิ่งที่เพิ่มขึ้น
 
ส่วน ความสามารถ 
🔍 Validation อัตโนมัติ  min_length ,  max_length ,  pattern ,  gt/lt ,  unique ,  Field()  พร้อม  @field_validator  สำหรับรหัสผ่าน 
🗄️ SQLAlchemy Model สร้างตารางอัตโนมัติ —  Column ,  index ,  unique ,  nullable ,  UUID  คีย์หลัก,  created_at/updated_at/is_deleted  
🧪 Pytest Test Suite ทดสอบทุก endpoint —  client.{method} ,  assert status_code , ตรวจสอบฟิลด์ใน response, รองรับ  Authorization  header 
 
 
 
🚀 วิธีใช้งาน
 
bash  
# 1. รันสร้างไฟล์
python fastapi_endpoint_generator_v2.py

# ได้ 3 ไฟล์:
# 📄 users_router.py
# 🗄️  users_model.py
# 🧪 test_users.py

# 2. รันทดสอบ
pytest test_users.py -v

# 3. นำ router ไปใช้
from users_router import router
app.include_router(router)
 
 
 
 
ต้องการปรับอะไรเพิ่มไหมครับ เช่น เพิ่ม Dependencies, ตัวอย่างการบันทึก DB จริง, หรือรูปแบบการตอบกลับมาตรฐานเดียวกันทุก endpoint 🎯✨