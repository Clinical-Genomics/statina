from NIPTool.adapter.plugin import NiptAdapter
from pymongo import MongoClient

def get_config():
    return {'DB_URI': 'mongodb://localhost:27030', 'DB_NAME': 'nipt-stage'}


def get_nipt_adapter():
    config = get_config()
    client = MongoClient(config['DB_URI'])
    return NiptAdapter(client, db_name=config['DB_NAME'])

