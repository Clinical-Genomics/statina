from typing import Optional, Literal, List, Iterable

from pydantic import parse_obj_as

from statina.adapter import StatinaAdapter
from statina.constants import sort_table, sample_sort_keys
from statina.crud.utils import paginate
from statina.models.database import DataBaseSample


def get_sample_text_query(query_string: str) -> dict:
    """Text search with regex, case insensitive"""
    return {
        "$or": [
            {"batch_id": {"$regex": query_string, "$options": "i"}},
            {"sample_id": {"$regex": query_string, "$options": "i"}},
            {"comment": {"$regex": query_string, "$options": "i"}},
            {"SampleType": {"$regex": query_string, "$options": "i"}},
            {"QCFlag": {"$regex": query_string, "$options": "i"}},
        ]
    }


def samples(
    adapter: StatinaAdapter,
) -> List[DataBaseSample]:
    """Return all samples from the sample collection"""
    raw_samples: Iterable[dict] = adapter.sample_collection.find()
    return parse_obj_as(List[DataBaseSample], list(raw_samples))


def query_samples(
    adapter: StatinaAdapter,
    batch_id: Optional[str] = None,
    sort_key: Optional[sample_sort_keys] = "sample_id",
    sort_direction: Optional[Literal["ascending", "descending"]] = "descending",
    query_string: Optional[str] = "",
    page_size: int = 0,
    page_num: int = 0,
) -> List[DataBaseSample]:
    """
    Query samples from the sample collection.
    Pagination can be enabled with <page_size> and <page_num> options.
    No pagination enabled by default.
    """
    skip, limit = paginate(page_size=page_size, page_num=page_num)
    raw_samples: Iterable[dict] = (
        adapter.sample_collection.find(
            {
                "$and": [
                    {"batch_id": batch_id or {"$regex": ".*"}},
                    get_sample_text_query(query_string=query_string),
                ],
            }
        )
        .sort(sort_key, sort_table.get(sort_direction))
        .skip(skip)
        .limit(limit)
    )
    return parse_obj_as(List[DataBaseSample], list(raw_samples))


def count_query_samples(
    adapter: StatinaAdapter, batch_id: Optional[str] = None, query_string: Optional[str] = ""
) -> int:
    """Count all queried samples in sample collection"""
    return adapter.sample_collection.count_documents(
        filter={
            "$and": [
                {"batch_id": batch_id or {"$regex": ".*"}},
                get_sample_text_query(query_string=query_string),
            ],
        }
    )


def sample(adapter: StatinaAdapter, sample_id: str) -> Optional[DataBaseSample]:
    """Find one sample from the sample collection"""

    raw_sample = adapter.sample_collection.find_one({"sample_id": sample_id})
    if not raw_sample:
        return None

    return DataBaseSample(**raw_sample)


def sample_aggregate(adapter: StatinaAdapter, pipe: list) -> list:
    """Aggregates a query pipeline on the sample collection"""

    return list(adapter.sample_collection.aggregate(pipe))


def batch_samples(
    adapter: StatinaAdapter,
    batch_id: str,
) -> List[DataBaseSample]:
    """All samples within the batch"""
    raw_samples: Iterable[dict] = adapter.sample_collection.find({"batch_id": batch_id})
    return parse_obj_as(List[DataBaseSample], list(raw_samples))


def query_batch_samples(
    adapter: StatinaAdapter,
    batch_id: str,
    page_size: int = 0,
    page_num: int = 0,
    sort_key: Optional[sample_sort_keys] = "sample_id",
    sort_direction: Optional[Literal["ascending", "descending"]] = "descending",
    query_string: Optional[str] = "",
) -> List[DataBaseSample]:
    """
    Query samples within the batch.
    Pagination can be enabled with <page_size> and <page_num> options.
    No pagination enabled by default.
    """
    skip, limit = paginate(page_size=page_size, page_num=page_num)
    raw_samples: Iterable[dict] = (
        adapter.sample_collection.find(
            {
                "$and": [{"batch_id": batch_id}, get_sample_text_query(query_string=query_string)],
            }
        )
        .sort(sort_key, sort_table.get(sort_direction))
        .skip(skip)
        .limit(limit)
    )
    return parse_obj_as(List[DataBaseSample], list(raw_samples))


def count_query_batch_samples(
    adapter: StatinaAdapter, batch_id: str, query_string: Optional[str] = ""
) -> int:
    """Count queried samples within the batch"""
    return adapter.sample_collection.count_documents(
        filter={
            "$and": [{"batch_id": batch_id}, get_sample_text_query(query_string=query_string)],
        }
    )
