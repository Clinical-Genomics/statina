from typing import Iterable, List, Optional

from pydantic import parse_obj_as

from statina.adapter import StatinaAdapter
from statina.crud.utils import paginate
from statina.models.database import Batch, DataBaseSample, User


def users(adapter: StatinaAdapter, page_size: int = 0, page_num: int = 0) -> List[User]:
    """Return all users from the batch collection"""
    skip, limit = paginate(page_size=page_size, page_num=page_num)
    users: Iterable[dict] = adapter.user_collection.find().skip(skip).limit(limit)
    return parse_obj_as(List[User], list(users))


def count_users(adapter: StatinaAdapter) -> int:
    """Count all users from the batch collection"""
    return adapter.user_collection.count_documents(filter={})


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


def samples(adapter: StatinaAdapter, page_size: int = 0, page_num: int = 0) -> List[DataBaseSample]:
    """Return all samples from the sample collection"""
    skip, limit = paginate(page_size=page_size, page_num=page_num)
    raw_samples: Iterable[dict] = adapter.sample_collection.find().skip(skip).limit(limit)
    return parse_obj_as(List[DataBaseSample], list(raw_samples))


def count_samples(adapter: StatinaAdapter) -> int:
    """Count all samples in sample collection"""
    return adapter.sample_collection.count_documents(filter={})


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


def batches(adapter: StatinaAdapter, page_size: int = 0, page_num: int = 0) -> List[Batch]:
    """Return all batches from the batch collection"""
    skip, limit = paginate(page_size=page_size, page_num=page_num)
    raw_batches: Iterable[dict] = adapter.batch_collection.find().skip(skip).limit(limit)
    return parse_obj_as(List[Batch], list(raw_batches))


def count_batches(adapter: StatinaAdapter) -> int:
    """Count all batches from the batch collection"""
    return adapter.batch_collection.count_documents(filter={})


def sample_aggregate(adapter: StatinaAdapter, pipe: list) -> list:
    """Aggregates a query pipeline on the sample collection"""

    return list(adapter.sample_collection.aggregate(pipe))


def batch_aggregate(adapter: StatinaAdapter, pipe: list) -> List[Batch]:
    """Aggregates a query pipeline on the sample collection"""

    return list(adapter.batch_collection.aggregate(pipe))


def batch_samples(
    adapter: StatinaAdapter, batch_id: str, page_size: int = 0, page_num: int = 0
) -> List[DataBaseSample]:
    """All samples within the batch"""
    skip, limit = paginate(page_size=page_size, page_num=page_num)
    raw_samples: Iterable[dict] = (
        adapter.sample_collection.find({"batch_id": batch_id}).skip(skip).limit(limit)
    )
    return parse_obj_as(List[DataBaseSample], list(raw_samples))


def count_batch_samples(adapter: StatinaAdapter, batch_id: str) -> int:
    """Count samples within the batch"""
    return adapter.sample_collection.count_documents(filter={"batch_id": batch_id})
