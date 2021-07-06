from pathlib import Path

from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings, EmailStr
from pymongo import MongoClient

from statina.adapter.plugin import StatinaAdapter

NIPT_PACKAGE = Path(__file__).parent
PACKAGE_ROOT: Path = NIPT_PACKAGE.parent
ENV_FILE: Path = PACKAGE_ROOT / ".env"
TEMPLATES_DIR: Path = NIPT_PACKAGE / "API" / "external" / "api" / "api_v1" / "templates"


class Settings(BaseSettings):
    """Settings for serving the statina app and connect to the mongo database"""

    db_uri: str = "mongodb://localhost:27017/statina-demo"
    db_name: str = "statina-demo"
    secret_key: str = "dummy"
    algorithm: str = "ABC"
    host: str = "localhost"
    access_token_expire_minutes: int = 60
    port: int = 8000

    class Config:
        env_file = str(ENV_FILE)


class EmailSettings(BaseSettings):
    """Settings for sending email"""

    sll_port: int = 465
    smtp_server: str = "smtp.gmail.com"
    sender_email: EmailStr
    sender_password: str

    class Config:
        env_file = str(ENV_FILE)


settings = Settings()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def get_nipt_adapter():
    client = MongoClient(settings.db_uri)
    return StatinaAdapter(client, db_name=settings.db_name)
