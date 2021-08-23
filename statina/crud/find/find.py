from typing import Iterable, List, Optional

from pydantic import parse_obj_as

from statina.adapter import StatinaAdapter
from statina.models.database import Batch, DataBaseSample, User


def users(adapter: StatinaAdapter) -> List[User]:
    """Return all users from the batch collection"""

    users: Iterable[dict] = adapter.user_collection.find()
    return parse_obj_as(List[User], list(users))


def user(
    adapter: StatinaAdapter, email: Optional[str] = None, user_name: Optional[str] = None
) -> Optional[User]:
    """Find user from user collection"""
    if email:
        raw_user: dict = adapter.user_collection.find_one({"email": email})  # ????? wierd
    elif user_name:
        raw_user: dict = adapter.user_collection.find_one({"username": user_name})
    else:
        raise SyntaxError("Have to use email or user_name")
    if not raw_user:
        return None
    return User(**raw_user)


def samples(adapter: StatinaAdapter) -> List[DataBaseSample]:
    """Return all batches from the batch collection"""

    raw_samples: Iterable[dict] = adapter.sample_collection.find()
    return parse_obj_as(List[DataBaseSample], list(raw_samples))


def sample(adapter: StatinaAdapter, sample_id: str) -> Optional[DataBaseSample]:
    """Find one sample from the sample collection"""

    raw_sample = adapter.sample_collection.find_one({"sample_id": sample_id})
    if not raw_sample:
        return None

    return DataBaseSample(**raw_sample)


def batch(adapter: StatinaAdapter, batch_id: str) -> Optional[Batch]:
    """Find one batch from the batch collection"""

    raw_batch: dict = adapter.batch_collection.find_one({"batch_id": batch_id})
    if not raw_batch:
        return None
    return Batch(**raw_batch)


def batches(adapter: StatinaAdapter) -> List[Batch]:
    """Return all batches from the batch collection"""

    raw_batches: Iterable[dict] = adapter.batch_collection.find()
    return parse_obj_as(List[Batch], list(raw_batches))


def sample_aggregate(adapter: StatinaAdapter, pipe: list) -> list:
    """Aggregates a query pipeline on the sample collection"""

    return list(adapter.sample_collection.aggregate(pipe))


def batch_aggregate(adapter: StatinaAdapter, pipe: list) -> List[Batch]:
    """Aggregates a query pipeline on the sample collection"""

    return list(adapter.batch_collection.aggregate(pipe))


def batch_samples(adapter: StatinaAdapter, batch_id: str) -> List[DataBaseSample]:
    """All samples within the batch"""

    raw_samples: Iterable[dict] = adapter.sample_collection.find({"batch_id": batch_id})
    return parse_obj_as(List[DataBaseSample], list(raw_samples))
