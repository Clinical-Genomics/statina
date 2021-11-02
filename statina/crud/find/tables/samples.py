from typing import Optional, Literal, List, Iterable

from pydantic import parse_obj_as

from statina.adapter import StatinaAdapter
from statina.constants import sort_table
from statina.crud.utils import paginate
from statina.models.database import DataBaseSample

SORT_KEYS = Literal[
            "sample_id",
            "batch_id",
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

def samples(
    adapter: StatinaAdapter,
    sort_key: Optional[SORT_KEYS] = "sample_id",
    sort_direction: Optional[Literal["ascending", "descending"]] = "descending",
    text: Optional[str] = "",
    page_size: int = 0,
    page_num: int = 0,
) -> List[DataBaseSample]:
    """Return all samples from the sample collection"""
    skip, limit = paginate(page_size=page_size, page_num=page_num)
    raw_samples: Iterable[dict] = (
        adapter.sample_collection.find(
            {
                "$or": [
                    {"batch_id": {"$regex": text, "$options": "i"}},
                    {"sample_id": {"$regex": text, "$options": "i"}},
                    {"comment": {"$regex": text, "$options": "i"}},
                    {"SampleType": {"$regex": text, "$options": "i"}},
                    {"QCFlag": {"$regex": text, "$options": "i"}},
                ]
            }
        )
        .sort(sort_key, sort_table.get(sort_direction))
        .skip(skip)
        .limit(limit)
    )
    return parse_obj_as(List[DataBaseSample], list(raw_samples))


def count_samples(adapter: StatinaAdapter, text: Optional[str] = "") -> int:
    """Count all samples in sample collection"""
    return adapter.sample_collection.count_documents(
        filter={
            "$or": [
                {"batch_id": {"$regex": text, "$options": "i"}},
                {"sample_id": {"$regex": text, "$options": "i"}},
                {"comment": {"$regex": text, "$options": "i"}},
                {"SampleType": {"$regex": text, "$options": "i"}},
                {"QCFlag": {"$regex": text, "$options": "i"}},
            ]
        }
    )


