from NIPTool.adapter.plugin import NiptAdapter
from pymongo import MongoClient
from pydantic import BaseSettings


class Settings(BaseSettings):
    db_uri: str = "test_uri"
    db_name: str = "test_db"


settings = Settings()


def get_nipt_adapter():
    client = MongoClient(settings.db_uri)
    return NiptAdapter(client, db_name=settings.db_name)
