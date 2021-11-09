from typing import Optional, Literal

from pydantic import BaseModel

from statina.constants import sample_sort_keys


class ListQuery(BaseModel):
    page_size: Optional[int] = 5
    page_num: Optional[int] = 0
    sort_direction: Optional[Literal["ascending", "descending"]] = "descending"
    query_string: Optional[str] = ""
    sort_key: Optional[sample_sort_keys] = ""


class BatchesQuery(ListQuery):
    sort_key: Optional[
        Literal["batch_id", "SequencingDate", "Flowcell", "comment"]
    ] = "SequencingDate"


class BatchSamplesQuery(ListQuery):
    batch_id: str
    sort_key: Optional[sample_sort_keys] = "sample_id"


class SamplesQuery(ListQuery):
    batch_id: Optional[str] = None
    sort_key: Optional[sample_sort_keys] = "sample_id"
