import logging
from typing import Dict, List, Optional

from NIPTool.adapter import NiptAdapter
from NIPTool.exeptions import InsertError
from NIPTool.models.database import Batch, Sample
from NIPTool.models.server.load import BatchRequestBody, UserRequestBody
from NIPTool.parse.batch import parse_segmental_calls
from pymongo.results import InsertManyResult, InsertOneResult

LOG = logging.getLogger(__name__)


def insert_batch(adapter: NiptAdapter, batch: Batch, batch_files: BatchRequestBody) -> str:
    """Load a batch into the database"""

    batch_dict = batch.dict(exclude_none=True)
    batch_dict["segmental_calls"] = batch_files.segmental_calls
    batch_dict["multiqc_report"] = batch_files.multiqc_report
    batch_dict["result_file"] = batch_files.result_file
    try:
        result: InsertOneResult = adapter.batch_collection.insert_one(batch_dict)
        LOG.info("Added document %s.", batch_dict["batch_id"])
    except:
        raise InsertError(message=f"Batch {batch.batch_id} allready in database.")
    return result.inserted_id


def insert_samples(
    adapter: NiptAdapter, samples: List[Sample], segmental_calls: Optional[str]
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
        raise InsertError(f"Sample keys allready in database.")
    return result.inserted_ids


def insert_user(adapter: NiptAdapter, user: UserRequestBody) -> str:
    """Function to load a new user to the database."""

    user_dict = {
        "email": user.email,
        "username": user.username,
        "role": user.role,
    }
    try:
        result: InsertOneResult = adapter.user_collection.insert_one(user_dict)
        LOG.info("Added user documen %s.", user.email)
    except:
        raise InsertError(f"User {user.email} already in database.")
    return result.inserted_id
