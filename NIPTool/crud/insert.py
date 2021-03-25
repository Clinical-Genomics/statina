import logging
from typing import Dict, List, Optional

from NIPTool.adapter import NiptAdapter
from NIPTool.models.database import Batch, Sample
from NIPTool.models.server.load import BatchRequestBody, UserRequestBody
from NIPTool.parse.batch import parse_segmental_calls
from pymongo.results import InsertManyResult, InsertOneResult

LOG = logging.getLogger(__name__)


def load_batch(adapter: NiptAdapter, batch: Batch, batch_files: BatchRequestBody) -> str:
    """Load a batch into the database"""

    batch_dict = batch.dict(exclude_none=True)
    batch_dict["_id"] = batch_dict["SampleProject"]
    batch_dict["segmental_calls"] = batch_files.segmental_calls
    batch_dict["multiqc_report"] = batch_files.multiqc_report
    batch_dict["result_file"] = batch_files.result_file
    result: InsertOneResult = adapter.batch_collection.insert_one(batch_dict)
    return result.inserted_id


def sample_to_dict(sample_object: Sample, segmental_calls: Optional[str]) -> dict:
    """Convert a sample object to a dict to insert into database"""
    sample_dict: dict = sample_object.dict(exclude_none=True)
    sample_id = sample_dict["SampleID"]
    sample_dict["_id"] = sample_id
    sample_dict["segmental_calls"] = segmental_calls
    return sample_dict


def load_sample(adapter: NiptAdapter, sample: Sample, segmental_calls: Optional[str]) -> str:
    """Load a sample into the database

    Return the sample id
    """
    result: InsertOneResult = adapter.sample_collection.insert_one(
        sample_to_dict(sample_object=sample, segmental_calls=segmental_calls)
    )
    return result.inserted_id


def load_samples(
    adapter: NiptAdapter, samples: List[Sample], segmental_calls: Optional[str]
) -> List[str]:
    """Function to load data from fluffy result file."""

    segmental_calls: Dict[str, str] = parse_segmental_calls(segmental_calls_path=segmental_calls)
    result: InsertManyResult = adapter.sample_collection.insert_many(
        [
            sample_to_dict(
                sample_object=sample, segmental_calls=segmental_calls.get(sample.SampleID)
            )
            for sample in samples
        ]
    )

    return result.inserted_ids


def load_user(adapter: NiptAdapter, user: UserRequestBody) -> str:
    """Function to load a new user to the database."""

    user = {"_id": user.email, "email": user.email, "name": user.name, "role": user.role}
    result: InsertOneResult = adapter.user_collection.insert_one(user)
    return result.inserted_id
