from pathlib import Path
from typing import Optional

from pydantic import BaseSettings
from pymongo import MongoClient

from statina.adapter.plugin import StatinaAdapter

NIPT_PACKAGE = Path(__file__).parent
PACKAGE_ROOT: Path = NIPT_PACKAGE.parent
ENV_FILE: Path = PACKAGE_ROOT / ".env"


class Settings(BaseSettings):
    """Settings for serving the statina app and connect to the mongo database"""

    db_uri: str = "mongodb://localhost:27017/statina-demo"
    db_name: str = "statina-demo"
    secret_key: str = "dummy"
    algorithm: str = "ABC"
    host: str = "localhost"
    access_token_expire_minutes: int = 15
    port: int = 8000
    admin_email: Optional[str]
    sender_prefix: Optional[str]
    mail_uri: Optional[str]
    website_uri: Optional[str]
    email_server_alias: Optional[str]

    class Config:
        env_file = str(ENV_FILE)


settings = Settings()


def get_nipt_adapter():
    client = MongoClient(settings.db_uri)
    return StatinaAdapter(client, db_name=settings.db_name)
