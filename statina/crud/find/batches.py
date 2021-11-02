from typing import Iterable, List, Optional, Literal

from pydantic import parse_obj_as

from statina.adapter import StatinaAdapter
from statina.constants import sort_table
from statina.crud.utils import paginate
from statina.models.database import Batch


def get_batches_query(text: str) -> dict:
    return {
        "$or": [
            {"batch_id": {"$regex": text, "$options": "i"}},
            {"comment": {"$regex": text, "$options": "i"}},
            {"Flowcell": {"$regex": text, "$options": "i"}},
        ]
    }


def batch(adapter: StatinaAdapter, batch_id: str) -> Optional[Batch]:
    """Find one batch from the batch collection"""

    raw_batch: dict = adapter.batch_collection.find_one({"batch_id": batch_id})
    if not raw_batch:
        return None
    return Batch(**raw_batch)


def batches(
    adapter: StatinaAdapter,
) -> List[Batch]:
    """Return all batches from the batch collection"""
    raw_batches: Iterable[dict] = adapter.batch_collection.find()
    return parse_obj_as(List[Batch], list(raw_batches))


def query_batches(
    adapter: StatinaAdapter,
    page_size: int = 0,
    page_num: int = 0,
    sort_direction: Optional[Literal["ascending", "descending"]] = "descending",
    sort_key: Optional[
        Literal["batch_id", "SequencingDate", "Flowcell", "comment"]
    ] = "SequencingDate",
    text: Optional[str] = "",
) -> List[Batch]:
    """Query batches from the batch collection"""
    skip, limit = paginate(page_size=page_size, page_num=page_num)
    raw_batches: Iterable[dict] = (
        adapter.batch_collection.find(get_batches_query(text=text))
        .sort(sort_key, sort_table.get(sort_direction))
        .skip(skip)
        .limit(limit)
    )
    return parse_obj_as(List[Batch], list(raw_batches))


def count_query_batches(adapter: StatinaAdapter, text: Optional[str] = "") -> int:
    """Count all queried batches from the batch collection"""
    return adapter.batch_collection.count_documents(filter=get_batches_query(text=text))


def batch_aggregate(adapter: StatinaAdapter, pipe: list) -> List[Batch]:
    """Aggregates a query pipeline on the sample collection"""

    return list(adapter.batch_collection.aggregate(pipe))
