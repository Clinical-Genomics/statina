from typing import Optional, Literal, List, Iterable

from pydantic import parse_obj_as

from statina.adapter import StatinaAdapter
from statina.constants import sort_table
from statina.crud.utils import paginate
from statina.models.database import DataBaseSample

SORT_KEYS = Literal[
            "sample_id",
            "Zscore_13",
            "Zscore_18",
            "Zscore_21",
            "Zscore_X",
            "FF_Formatted",
            "CNVSegment",
            "FFY",
            "FFX",
            "comment",
            "QCFlag",
        ]

def batch_samples(
    adapter: StatinaAdapter,
    batch_id: str,
    page_size: int = 0,
    page_num: int = 0,
    sort_key: Optional[SORT_KEYS] = "sample_id",
    sort_direction: Optional[Literal["ascending", "descending"]] = "descending",
    text: Optional[str] = "",
) -> List[DataBaseSample]:
    """All samples within the batch"""
    skip, limit = paginate(page_size=page_size, page_num=page_num)
    raw_samples: Iterable[dict] = (
        adapter.sample_collection.find(
            {
                "$and": [
                    {"batch_id": batch_id},
                    {
                        "$or": [
                            {"sample_id": {"$regex": text, "$options": "i"}},
                            {"comment": {"$regex": text, "$options": "i"}},
                            {"SampleType": {"$regex": text, "$options": "i"}},
                            {"QCFlag": {"$regex": text, "$options": "i"}},
                        ]
                    },
                ],
            }
        )
        .sort(sort_key, sort_table.get(sort_direction))
        .skip(skip)
        .limit(limit)
    )
    return parse_obj_as(List[DataBaseSample], list(raw_samples))


def count_batch_samples(adapter: StatinaAdapter, batch_id: str, text: Optional[str] = "") -> int:
    """Count samples within the batch"""
    return adapter.sample_collection.count_documents(
        filter={
            "$and": [
                {"batch_id": batch_id},
                {
                    "$or": [
                        {"sample_id": {"$regex": text, "$options": "i"}},
                        {"comment": {"$regex": text, "$options": "i"}},
                        {"SampleType": {"$regex": text, "$options": "i"}},
                        {"QCFlag": {"$regex": text, "$options": "i"}},
                    ]
                },
            ],
        }
    )