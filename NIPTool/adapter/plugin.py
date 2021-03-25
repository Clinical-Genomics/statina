import logging
from datetime import datetime as dt

from mongo_adapter import MongoAdapter
from pymongo.collection import Collection
from pymongo.database import Database

LOG = logging.getLogger(__name__)


class NiptAdapter(MongoAdapter):
    def setup(self, db_name: str):
        """Setup connection to a database"""

        if self.client is None:
            raise SyntaxError("No client is available")
        self.db: Database = self.client[db_name]
        self.db_name: str = db_name
        self.sample_collection: Collection = self.db.sample
        self.batch_collection: Collection = self.db.batch
        self.user_collection: Collection = self.db.user

        LOG.info("Use database %s.", db_name)

    def add_or_update_document(self, document_news: dict, collection):
        """Adds/updates a document in the database"""

        document_id = document_news.get("_id")
        if not document_id:
            document_id = collection.insert(document_news)
            LOG.info("Added document %s.", document_id)
        else:
            update_result = collection.update_one(
                {"_id": document_id}, {"$set": document_news}, upsert=True
            )
            if not update_result.raw_result["updatedExisting"]:
                collection.update_one({"_id": document_id}, {"$set": {"added": dt.today()}})
                LOG.info("Added document %s.", document_id)
            elif update_result.modified_count:
                collection.update_one({"_id": document_id}, {"$set": {"updated": dt.today()}})
                LOG.info("Updated document %s.", document_id)
            else:
                LOG.info("No updates for document %s.", document_id)
        return document_id
