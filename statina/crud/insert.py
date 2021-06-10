import logging
from typing import Dict, List, Optional

from pymongo.results import InsertManyResult, InsertOneResult

from statina.adapter import StatinaAdapter
from statina.exeptions import InsertError
from statina.models.database import Batch, DataBaseSample, User
from statina.models.server.load import BatchRequestBody
from statina.parse.batch import parse_segmental_calls

LOG = logging.getLogger(__name__)


def insert_batch(adapter: StatinaAdapter, batch: Batch, batch_files: BatchRequestBody) -> str:
    """Load a batch into the database"""

    batch_dict = batch.dict(exclude_none=True)
    batch_dict["segmental_calls"] = batch_files.segmental_calls
    batch_dict["multiqc_report"] = batch_files.multiqc_report
    batch_dict["result_file"] = batch_files.result_file
    try:
        result: InsertOneResult = adapter.batch_collection.insert_one(batch_dict)
        LOG.info("Added document %s.", batch_dict["batch_id"])
    except:
        raise InsertError(message=f"Batch {batch.batch_id} already in database.")
    return result.inserted_id


def insert_samples(
    adapter: StatinaAdapter, samples: List[DataBaseSample], segmental_calls: Optional[str]
) -> List[str]:
    """Function to load data from fluffy result file."""

    segmental_calls: Dict[str, str] = parse_segmental_calls(segmental_calls_path=segmental_calls)
    sample_dicts = []
    for sample in samples:
        sample_dict: dict = sample.dict(exclude_none=True)
        sample_dict["segmental_calls"] = segmental_calls.get(sample.sample_id)
        sample_dicts.append(sample_dict)
    try:
        result: InsertManyResult = adapter.sample_collection.insert_many(sample_dicts)
        LOG.info("Added sample documents.")
    except:
        raise InsertError(f"Sample keys already in database.")
    return result.inserted_ids


def insert_user(adapter: StatinaAdapter, user: User) -> str:
    """Function to load a new user to the database."""

    existing_user: Optional[dict] = adapter.user_collection.find(
        {"$or": [{"username": user.username}, {"email": user.email}]}
    )
    if list(existing_user):
        raise InsertError(
            f"User with username {user.username} or email {user.email} already exist in database."
        )
    try:
        result: InsertOneResult = adapter.user_collection.insert_one(user.dict())
        LOG.info("Added user document %s.", user.email)
    except:
        raise InsertError(f"User {user.email} already in database.")
    return result.inserted_id
