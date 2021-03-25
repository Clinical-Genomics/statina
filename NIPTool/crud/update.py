import logging

from NIPTool.adapter import NiptAdapter
from NIPTool.models.database import Sample

LOG = logging.getLogger(__name__)


def sample(adapter: NiptAdapter, sample_object: Sample) -> dict:
    """Update a sample object in the database"""
    sample_dict: dict = sample_object.dict(exclude_none=True)
    sample_id = sample_dict["SampleID"]
    LOG.info("Updating sample %s", sample_id)
    sample_dict["_id"] = sample_id
    adapter.sample_collection.update_one({"_id": sample_id}, sample_dict)
    return sample_dict
