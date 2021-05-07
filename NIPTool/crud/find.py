from typing import Iterable, List, Optional

from NIPTool.adapter import NiptAdapter
from NIPTool.models.database import Batch, Sample, User

from pydantic import parse_obj_as


def user(
    adapter: NiptAdapter, email: Optional[str] = None, user_name: Optional[str] = None
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


def sample(adapter: NiptAdapter, sample_id: str) -> Optional[Sample]:
    """Find one sample from the sample collection"""

    raw_sample = adapter.sample_collection.find_one({"sample_id": sample_id})
    if not raw_sample:
        return None

    return Sample(**raw_sample)


def batch(adapter: NiptAdapter, batch_id: str) -> Optional[Batch]:
    """Find one batch from the batch collection"""

    raw_batch: dict = adapter.batch_collection.find_one({"batch_id": batch_id})
    if not raw_batch:
        return None
    return Batch(**raw_batch)


def batches(adapter: NiptAdapter) -> List[Batch]:
    """Return all batches from the batch collection"""

    raw_batches: Iterable[dict] = adapter.batch_collection.find()
    return parse_obj_as(List[Batch], list(raw_batches))


def sample_aggregate(adapter: NiptAdapter, pipe: list) -> list:
    """Aggregates a query pipeline on the sample collection"""

    return list(adapter.sample_collection.aggregate(pipe))


def batch_aggregate(adapter: NiptAdapter, pipe: list) -> List[Batch]:
    """Aggregates a query pipeline on the sample collection"""

    return list(adapter.batch_collection.aggregate(pipe))


def batch_samples(adapter: NiptAdapter, batch_id: str) -> List[Sample]:
    """All samples within the batch"""

    raw_samples: Iterable[dict] = adapter.sample_collection.find({"batch_id": batch_id})
    return parse_obj_as(List[Sample], list(raw_samples))
