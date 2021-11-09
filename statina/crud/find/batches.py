from typing import Iterable, List, Optional, Literal

from pydantic import parse_obj_as

from statina.adapter import StatinaAdapter
from statina.constants import sort_table
from statina.crud.utils import paginate
from statina.models.database import DatabaseBatch


def get_batches_text_query(query_string: str) -> dict:
    """Text search with regex, case insensitive"""
    return {
        "$or": [
            {"batch_id": {"$regex": query_string, "$options": "i"}},
            {"comment": {"$regex": query_string, "$options": "i"}},
            {"Flowcell": {"$regex": query_string, "$options": "i"}},
        ]
    }


def batch(adapter: StatinaAdapter, batch_id: str) -> Optional[DatabaseBatch]:
    """Find one batch from the batch collection"""

    raw_batch: dict = adapter.batch_collection.find_one({"batch_id": batch_id})
    if not raw_batch:
        return None
    return DatabaseBatch(**raw_batch)


def batches(
    adapter: StatinaAdapter,
) -> List[DatabaseBatch]:
    """Return all batches from the batch collection"""
    raw_batches: Iterable[dict] = adapter.batch_collection.find()
    return parse_obj_as(List[DatabaseBatch], list(raw_batches))


def query_batches(
    adapter: StatinaAdapter,
    page_size: int = 0,
    page_num: int = 0,
    sort_direction: Optional[Literal["ascending", "descending"]] = "descending",
    sort_key: Optional[
        Literal["batch_id", "SequencingDate", "Flowcell", "comment"]
    ] = "SequencingDate",
    query_string: Optional[str] = "",
) -> List[DatabaseBatch]:
    """
    Query batches from the batch collection.
    Pagination can be enabled with <page_size> and <page_num> options.
    No pagination enabled by default.
    """
    skip, limit = paginate(page_size=page_size, page_num=page_num)
    raw_batches: Iterable[dict] = (
        adapter.batch_collection.find(get_batches_text_query(query_string=query_string))
        .sort(sort_key, sort_table.get(sort_direction))
        .skip(skip)
        .limit(limit)
    )
    return parse_obj_as(List[DatabaseBatch], list(raw_batches))


def count_query_batches(adapter: StatinaAdapter, query_string: Optional[str] = "") -> int:
    """Count all queried batches from the batch collection"""
    return adapter.batch_collection.count_documents(
        filter=get_batches_text_query(query_string=query_string)
    )
