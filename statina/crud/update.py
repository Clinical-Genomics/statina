import logging

from statina.adapter import StatinaAdapter
from statina.models.database import DataBaseSample

LOG = logging.getLogger(__name__)


def sample(adapter: StatinaAdapter, sample: DataBaseSample) -> None:
    """Update a sample object in the database"""

    sample_dict: dict = sample.dict(exclude_none=True)
    sample_id = sample.sample_id
    LOG.info("Updating sample %s", sample_id)
    adapter.sample_collection.update_one({"sample_id": sample_id}, {"$set": sample_dict})
