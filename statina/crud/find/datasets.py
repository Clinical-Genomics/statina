from typing import Optional

from statina.adapter import StatinaAdapter
from statina.models.database.dataset import Dataset


def get_dataset(
    adapter: StatinaAdapter, batch_id: Optional[str], name: Optional[str]
) -> Optional[Dataset]:
    if batch_id:
        batch: dict = adapter.batch_collection.find_one({"batch_id": batch_id})
        if not batch:
            return None
        if not batch.get("dataset"):
            return None
    dataset = adapter.dataset_collection.find({"name": batch.get("dataset")})
    if not dataset:
        return None
    return Dataset(**dict(dataset))
