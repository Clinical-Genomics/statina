import logging
from typing import Dict, List, Optional

from NIPTool.adapter import NiptAdapter
from NIPTool.models.database import Batch, Sample
from NIPTool.models.server.load import BatchRequestBody, UserRequestBody
from NIPTool.parse.batch import parse_segmental_calls

LOG = logging.getLogger(__name__)


def load_batch(adapter: NiptAdapter, batch: Batch, batch_files: BatchRequestBody) -> dict:
    """Load a batch into the database"""

    batch_dict = batch.dict(exclude_none=True)
    batch_dict["_id"] = batch_dict["SampleProject"]
    batch_dict["segmental_calls"] = batch_files.segmental_calls
    batch_dict["multiqc_report"] = batch_files.multiqc_report
    batch_dict["result_file"] = batch_files.result_file
    adapter.batch_collection.insert_one(batch_dict)
    return batch_dict


def load_sample(adapter: NiptAdapter, sample: Sample, segmental_calls: Optional[str]) -> dict:
    """Load a sample into the database"""
    sample_dict: dict = sample.dict(exclude_none=True)
    sample_id = sample_dict["SampleID"]
    sample_dict["_id"] = sample_id
    sample_dict["segmental_calls"] = segmental_calls
    adapter.sample_collection.insert_one(sample_dict)
    return sample_dict


def load_samples(
    adapter: NiptAdapter, samples: List[Sample], segmental_calls: Optional[str]
) -> List[dict]:
    """Function to load data from fluffy result file."""

    segmental_calls: Dict[str, str] = parse_segmental_calls(segmental_calls_path=segmental_calls)
    inserted_samples: List[dict] = []
    for sample in samples:
        inserted_samples.append(
            load_sample(
                adapter=adapter, sample=sample, segmental_calls=segmental_calls.get(sample.SampleID)
            )
        )
    return inserted_samples


def load_user(adapter: NiptAdapter, user: UserRequestBody) -> dict:
    """Function to load a new user to the database."""

    user = {"_id": user.email, "email": user.email, "name": user.name, "role": user.role}
    adapter.user_collection.insert_one(user)
    return user
