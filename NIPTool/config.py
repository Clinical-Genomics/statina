import pkg_resources
from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings
from pymongo import MongoClient

from NIPTool.adapter.plugin import NiptAdapter


class Settings(BaseSettings):
    db_uri: str = "mongodb://localhost:27017/nipt-demo"
    db_name: str = "nipt-demo"
    host: str = "localhost"
    port: int = 8000

    class Config:
        from_file = pkg_resources.resource_filename("NIPTool", ".env")


settings = Settings()
templates = Jinja2Templates(directory="./NIPTool/API/external/api/api_v1/templates")


def get_nipt_adapter():
    print("hej")
    print(settings)
    client = MongoClient(settings.db_uri)
    return NiptAdapter(client, db_name=settings.db_name)
