"""Security - encryption at rest status."""
from fastapi import APIRouter

from ..db import db

router = APIRouter(prefix="/security", tags=["security"])


@router.get("/encryption")
def encryption_status():
    return {
        "encrypt_at_rest": db.encryption_active,
        "mode": "fernet-aes128" if db.encryption_active else "plaintext",
        "hint": "Enable with ENCRYPT_AT_REST=1 (and set ENCRYPTION_KEY or let it generate one)",
    }
