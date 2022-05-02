from typing import Optional

from statina.adapter import StatinaAdapter
from statina.config import base_dataset_thresholds
from statina.models.database.dataset import Dataset


def get_dataset(
    adapter: StatinaAdapter, batch_id: Optional[str] = None, name: Optional[str] = None
) -> Optional[Dataset]:
    if name:
        dataset = adapter.dataset_collection.find({"name": name})
        return Dataset(**dict(dataset))
    if batch_id:
        batch: dict = adapter.batch_collection.find_one({"batch_id": batch_id})
        if not batch:
            return base_dataset_thresholds
        if not batch.get("dataset"):
            return base_dataset_thresholds
        dataset = adapter.dataset_collection.find({"name": batch.get("dataset")})
        if dataset:
            return Dataset(**dict(dataset))
