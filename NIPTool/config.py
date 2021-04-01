from pydantic import BaseSettings
from pymongo import MongoClient

from NIPTool.adapter.plugin import NiptAdapter


class Settings(BaseSettings):
    db_uri: str = "test_uri"
    db_name: str = "test_db"

    class Config:
        from_file = ".env"


settings = Settings()


def get_nipt_adapter():
    client = MongoClient(settings.db_uri)
    return NiptAdapter(client, db_name=settings.db_name)
