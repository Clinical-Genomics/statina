import logging

from NIPTool.adapter import NiptAdapter
from NIPTool.models.database import Sample

LOG = logging.getLogger(__name__)


def sample(adapter: NiptAdapter, sample: Sample) -> dict:
    """Update a sample object in the database"""

    sample_dict: dict = sample.dict(exclude_none=True)
    sample_id = sample.sample_id
    LOG.info("Updating sample %s", sample_id)
    adapter.sample_collection.update_one({"sample_id": sample_id}, {"$set": sample_dict})
    return sample_dict
