"""Settings via environment variables."""
import os
from pathlib import Path

from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def _bool_env(key: str, default: bool = False) -> bool:
    return os.environ.get(key, str(default)).lower() in ("1", "true", "yes", "on")


class Settings(BaseModel):
    app_name: str = "fastapi-obsidian-backend"
    data_dir: Path = DATA_DIR
    skills_dir: Path = DATA_DIR / "skills"
    encrypt_at_rest: bool = False
    encryption_key_env: str = "ENCRYPTION_KEY"
    jwt_secret_env: str = "JWT_SECRET"

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def load(cls) -> "Settings":
        data = Path(os.environ.get("DATA_DIR", str(DATA_DIR)))
        return cls(
            data_dir=data,
            skills_dir=Path(os.environ.get("SKILLS_DIR", str(data / "skills"))),
            encrypt_at_rest=_bool_env("ENCRYPT_AT_REST", False),
        )


settings = Settings.load()
