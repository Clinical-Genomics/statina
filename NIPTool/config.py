from pathlib import Path

from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings
from pymongo import MongoClient

from NIPTool.adapter.plugin import NiptAdapter

NIPT_PACKAGE = Path(__file__).parent
PACKAGE_ROOT: Path = NIPT_PACKAGE.parent
ENV_FILE: Path = PACKAGE_ROOT / ".env"
TEMPLATES_DIR: Path = NIPT_PACKAGE / "API" / "external" / "api" / "api_v1" / "templates"


class Settings(BaseSettings):
    """Settings for serving the nipt app and connect to the mongo database"""

    db_uri: str = "mongodb://localhost:27017/nipt-demo"
    db_name: str = "nipt-demo"
    host: str = "localhost"
    port: int = 8000

    class Config:
        env_file = str(ENV_FILE)


settings = Settings()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def get_nipt_adapter():
    client = MongoClient(settings.db_uri)
    return NiptAdapter(client, db_name=settings.db_name)
