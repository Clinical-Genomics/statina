import logging
from statina.adapter import StatinaAdapter
from statina.models.database import DataBaseSample, User

LOG = logging.getLogger(__name__)


def sample(adapter: StatinaAdapter, sample: DataBaseSample) -> None:
    """Update a sample object in the database"""

    sample_dict: dict = sample.dict(exclude_none=True)
    sample_id = sample.sample_id
    LOG.info("Updating sample %s", sample_id)
    adapter.sample_collection.update_one({"sample_id": sample_id}, {"$set": sample_dict})


def update_user(adapter: StatinaAdapter, user: User) -> None:
    """Update a user object in the database"""

    user_dict: dict = user.dict(exclude_none=True)
    email = user.email
    LOG.info(f"Updating user {email}")
    adapter.user_collection.update_one({"email": email}, {"$set": user_dict})
