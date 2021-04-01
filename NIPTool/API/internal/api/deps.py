from NIPTool.adapter.plugin import NiptAdapter
from pydantic import BaseSettings
from pymongo import MongoClient


class Settings(BaseSettings):
    db_uri: str = "test-uri"
    db_name: str = "test-db"

    class Config:
        env_file = ".env"


settings = Settings()


def get_nipt_adapter():
    client = MongoClient(settings.db_uri)
    print(settings)
    print(settings.db_uri)
    print(client)
    return NiptAdapter(client, db_name=settings.db_name)
