from typing import Optional, Literal, List, Any

from pydantic import BaseModel, validator

from statina.constants import sample_sort_keys
from statina.models.database import DataBaseSample
from statina.models.database.sample import DataBaseSampleOptionalFields


class ListQuery(BaseModel):
    page_size: Optional[int] = 5
    page_num: Optional[int] = 0
    sort_direction: Optional[Literal["ascend", "descend"]] = "descend"
    query_string: Optional[str] = ""
    sort_key: Optional[sample_sort_keys] = ""


class BatchesQuery(ListQuery):
    sort_key: Optional[
        Literal["batch_id", "SequencingDate", "Flowcell", "comment"]
    ] = "SequencingDate"


class BatchSamplesQuery(ListQuery):
    batch_id: str
    sort_key: Optional[sample_sort_keys] = "sample_id"


class FilterModel(BaseModel):
    column: Literal[
        "Zscore_13",
        "Zscore_18",
        "Zscore_21",
        "Zscore_X",
        "FFX",
        "FFY",
        "FF_Formatted",
        "CNVSegment",
        "status_13",
        "status_18",
        "status_21",
        "status_X0",
        "status_XXX",
        "status_XXY",
        "status_XYY",
        "include",
    ]
    rule: Literal["==", "!=", ">", "<", ">=", "<="]
    value: Any

    @validator("value", always=True)
    def validate_value(cls, v, values: dict):
        DataBaseSampleOptionalFields(**{values["column"]: v})
        return v


class SamplesQuery(ListQuery):
    batch_id: Optional[str] = None
    sort_key: Optional[sample_sort_keys] = "sample_id"
    filters: Optional[str]
