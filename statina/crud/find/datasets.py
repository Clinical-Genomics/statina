from typing import Optional, List, Iterable

from pydantic import parse_obj_as

from statina.adapter import StatinaAdapter
from statina.crud.utils import paginate
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
            return None
        if not batch.get("dataset"):
            return adapter.dataset_collection.find({"name": "default"})
        dataset = adapter.dataset_collection.find({"name": batch.get("dataset")})
        if dataset:
            return Dataset(**dict(dataset))


def get_datasets_text_query(query_string: str) -> dict:
    """Text search with regex, case insensitive"""
    return {
        "$or": [
            {"name": {"$regex": query_string, "$options": "i"}},
            {"comment": {"$regex": query_string, "$options": "i"}},
        ]
    }


def query_datasets(
    adapter: StatinaAdapter,
    page_size: int = 0,
    page_num: int = 0,
    query_string: Optional[str] = "",
) -> List[Dataset]:
    """
    Query batches from the batch collection.
    Pagination can be enabled with <page_size> and <page_num> options.
    No pagination enabled by default.
    """
    skip, limit = paginate(page_size=page_size, page_num=page_num)
    datasets: Iterable[dict] = (
        adapter.dataset_collection.find(get_datasets_text_query(query_string=query_string))
        .skip(skip)
        .limit(limit)
    )
    return parse_obj_as(List[Dataset], list(datasets))


def count_query_datasets(
    adapter: StatinaAdapter,
    query_string: Optional[str] = "",
) -> int:
    """
    Query batches from the batch collection.
    Pagination can be enabled with <page_size> and <page_num> options.
    No pagination enabled by default.
    """
    return adapter.dataset_collection.count_documents(
        filter=get_datasets_text_query(query_string=query_string)
    )
