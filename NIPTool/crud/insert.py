import logging
from typing import Dict, List, Optional

from NIPTool.adapter import NiptAdapter
from NIPTool.models.database import Batch, Sample
from NIPTool.models.server.load import BatchRequestBody, UserRequestBody
from NIPTool.parse.batch import parse_segmental_calls
from pymongo.results import InsertManyResult, InsertOneResult

LOG = logging.getLogger(__name__)


def insert_batch(adapter: NiptAdapter, batch: Batch, batch_files: BatchRequestBody) -> str:
    """Load a batch into the database"""

    batch_dict = batch.dict(exclude_none=True)
    batch_dict["_id"] = batch.batch_id
    batch_dict["segmental_calls"] = batch_files.segmental_calls
    batch_dict["multiqc_report"] = batch_files.multiqc_report
    batch_dict["result_file"] = batch_files.result_file
    result: InsertOneResult = adapter.batch_collection.insert_one(batch_dict)
    LOG.info("Added document %s.", batch_dict["batch_id"])
    return result.inserted_id


def sample_to_dict(sample: Sample, segmental_calls: Optional[str]) -> dict:
    """Convert a sample object to a dict to insert into database"""

    sample_dict: dict = sample.dict(exclude_none=True)
    sample_dict["_id"] = sample.sample_id
    sample_dict["segmental_calls"] = segmental_calls
    return sample_dict

def insert_samples(
        adapter: NiptAdapter, samples: List[Sample], segmental_calls: Optional[str]) -> List[str]:
    """Function to load data from fluffy result file."""

    segmental_calls: Dict[str, str] = parse_segmental_calls(segmental_calls_path=segmental_calls)
    mongo_samples = []
    for sample in samples:
        segmental_calls_path = segmental_calls.get(sample.sample_id)
        sample_dict = sample_to_dict(sample_object=sample, segmental_calls=segmental_calls_path)
        mongo_samples.append(sample_dict)

    result: InsertManyResult = adapter.sample_collection.insert_many(mongo_samples)
    LOG.info("Added sample documents.")
    return result.inserted_ids


def insert_user(adapter: NiptAdapter, user: UserRequestBody) -> str:
    """Function to load a new user to the database."""

    user_dict = {"_id": user.email, "email": user.email, "username": user.name, "role": user.role}
    result: InsertOneResult = adapter.user_collection.insert_one(user_dict)
    LOG.info("Added user documen %s.", user.email)
    return result.inserted_id
