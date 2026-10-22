# auth/webauthn.py
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
    base64url_to_bytes,
    bytes_to_base64url
)
from webauthn.helpers.structs import (
    PublicKeyCredentialRpEntity,
    PublicKeyCredentialUserEntity,
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement
)
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from .database import DBUser
import os

RP_ID = os.getenv("WEBAUTHN_RP_ID", "zyntroai.com")
RP_NAME = "ZyntroAI"

# ------------------------------
# ลงทะเบียน Passkey
# ------------------------------
def get_registration_options(user: DBUser):
    return generate_registration_options(
        rp=PublicKeyCredentialRpEntity(name=RP_NAME, id=RP_ID),
        user=PublicKeyCredentialUserEntity(
            id=str(uuid.uuid4()).encode(),
            name=user.email,
            display_name=user.full_name or user.email
        ),
        authenticator_selection=AuthenticatorSelectionCriteria(
            user_verification=UserVerificationRequirement.PREFERRED,
            resident_key=True
        ),
        exclude_credentials=[]
    )

# ------------------------------
# ตรวจสอบการล็อกอิน
# ------------------------------
def get_auth_options(user: DBUser = None):
    return generate_authentication_options(
        rp_id=RP_ID,
        user_verification=UserVerificationRequirement.PREFERRED
    )
