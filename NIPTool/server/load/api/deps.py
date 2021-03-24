from NIPTool.adapter.plugin import NiptAdapter
from pymongo import MongoClient
from pydantic import BaseSettings


class Settings(BaseSettings):
    db_uri: str
    db_name: str


settings = Settings()


def get_nipt_adapter():
    client = MongoClient(settings.db_uri)
    return NiptAdapter(client, db_name=settings.db_name)
