from typing import Optional, Literal, List, Iterable

from pydantic import parse_obj_as

from statina.adapter import StatinaAdapter
from statina.constants import sort_table
from statina.crud.utils import paginate
from statina.models.database import Batch


def batches(
    adapter: StatinaAdapter,
    page_size: int = 0,
    page_num: int = 0,
    sort_direction: Optional[Literal["ascending", "descending"]] = "descending",
    sort_key: Optional[
        Literal["batch_id", "SequencingDate", "Flowcell", "comment"]
    ] = "SequencingDate",
    text: Optional[str] = "",
) -> List[Batch]:
    """Return all batches from the batch collection"""
    skip, limit = paginate(page_size=page_size, page_num=page_num)
    raw_batches: Iterable[dict] = (
        adapter.batch_collection.find(
            {
                "$or": [
                    {"batch_id": {"$regex": text, "$options": "i"}},
                    {"comment": {"$regex": text, "$options": "i"}},
                    {"Flowcell": {"$regex": text, "$options": "i"}},
                ]
            }
        )
        .sort(sort_key, sort_table.get(sort_direction))
        .skip(skip)
        .limit(limit)
    )
    return parse_obj_as(List[Batch], list(raw_batches))


def count_batches(adapter: StatinaAdapter, text: Optional[str] = "") -> int:
    """Count all batches from the batch collection"""
    return adapter.batch_collection.count_documents(
        filter={
            "$or": [
                {"batch_id": {"$regex": text, "$options": "i"}},
                {"comment": {"$regex": text, "$options": "i"}},
                {"Flowcell": {"$regex": text, "$options": "i"}},
            ]
        }
    )