"""BytePlus client construction — credentials and connection only.

No business logic belongs in this file. It exists so that the SDK's
initialisation details are confined to one place.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


class MissingCredentialError(RuntimeError):
    """Raised when BytePlus credentials are absent from the environment."""


@dataclass
class BytePlusClient:
    """Holds credentials/region and (in a real deployment) the SDK handle."""

    access_key: str
    secret_key: str
    region: str = "ap-southeast-1"

    @classmethod
    def from_env(cls) -> BytePlusClient:
        access_key = os.environ.get("BYTEPLUS_ACCESS_KEY")
        secret_key = os.environ.get("BYTEPLUS_SECRET_KEY")
        missing = [
            name
            for name, value in (
                ("BYTEPLUS_ACCESS_KEY", access_key),
                ("BYTEPLUS_SECRET_KEY", secret_key),
            )
            if not value
        ]
        if missing:
            raise MissingCredentialError(
                "missing required environment variable(s): " + ", ".join(missing)
            )
        return cls(
            access_key=access_key,
            secret_key=secret_key,
            region=os.getenv("BYTEPLUS_REGION", "ap-southeast-1"),
        )

    def get_region(self) -> str:
        return self.region
