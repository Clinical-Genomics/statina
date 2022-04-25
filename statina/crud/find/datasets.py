from typing import Optional

from statina.adapter import StatinaAdapter
from statina.models.database.dataset import Dataset


def get_batch_dataset(adapter: StatinaAdapter, batch_id: str) -> Optional[Dataset]:
    batch: dict = adapter.batch_collection.find_one({"batch_id": batch_id})
    if not batch:
        return None
    if not batch.get("dataset"):
        return None
    dataset = adapter.dataset_collection.find({"name": batch.get("dataset")})
    return Dataset(**dataset)
