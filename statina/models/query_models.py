from typing import Optional, Literal

from fastapi import Query
from pydantic import BaseModel

from statina.constants import sample_sort_keys


class ListQuery(BaseModel):
    page_size: Optional[int] = Query(5)
    page_num: Optional[int] = Query(0)
    sort_direction: Optional[Literal["ascending", "descending"]] = Query("descending")
    query_string: Optional[str] = Query("")
    sort_key: Optional[sample_sort_keys] = Query("")


class BatchesQuery(ListQuery):
    sort_key: Optional[Literal["batch_id", "SequencingDate", "Flowcell", "comment"]] = Query(
        "SequencingDate"
    )


class BatchSamplesQuery(ListQuery):
    batch_id: str
    sort_key: Optional[sample_sort_keys] = Query("sample_id")
