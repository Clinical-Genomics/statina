from typing import Iterable, List

from NIPTool.adapter import NiptAdapter
from NIPTool.models.database import Batch, User, Sample


def user(adapter: NiptAdapter, user_name: str) -> User:
    """Find user from user collection"""
    raw_user: dict = adapter.user_collection.find_one({"_id": user_name})
    return User(**raw_user)


def sample_to_model(raw_sample: dict) -> Sample:
    raw_sample["SampleID"] = raw_sample.pop("_id")
    return Sample(**raw_sample)


def sample(adapter: NiptAdapter, sample_id: str) -> Sample:
    """Find one sample from the sample collection"""

    return adapter.sample_collection.find_one({"_id": sample_id})


def batch_to_model(raw_batch: dict) -> Batch:
    """Convert a database dict to batch object"""
    raw_batch["batch_id"] = raw_batch.pop("_id")
    return Batch(**raw_batch)


def batch(adapter: NiptAdapter, batch_id: str) -> Batch:
    """Find one batch from the batch collection"""
    raw_batch: dict = adapter.batch_collection.find_one({"_id": batch_id})
    return batch_to_model(raw_batch)


def batches(adapter: NiptAdapter) -> List[Batch]:
    """Return all batches from the batch collection"""
    raw_batches: Iterable[dict] = adapter.batch_collection.find()
    return [batch_to_model(raw_batch) for raw_batch in raw_batches]


def sample_aggregate(adapter: NiptAdapter, pipe: list) -> List[Sample]:
    """Aggregates a query pipeline on the sample collection"""
    raw_samples: Iterable[dict] = adapter.sample_collection.aggregate(pipe)
    return [sample_to_model(raw_sample) for raw_sample in raw_samples]


def batch_aggregate(adapter: NiptAdapter, pipe: list) -> List[Batch]:
    """Aggregates a query pipeline on the sample collection"""
    raw_batches: Iterable[dict] = adapter.batch_collection.aggregate(pipe)
    return [batch_to_model(raw_batch) for raw_batch in raw_batches]


def batch_samples(adapter: NiptAdapter, batch_id: str) -> List[Sample]:
    """All samples within the batch"""
    raw_samples: Iterable[dict] = adapter.sample_collection.find({"SampleProject": batch_id})
    return [sample_to_model(raw_sample) for raw_sample in raw_samples]
