from typing import List

from pydantic import BaseModel, validator


class CoveragePlotSampleData(BaseModel):
    """Sample data for coverage plot"""

    y_axis: List[float]
    x_axis: List[int]

    @validator("x_axis")
    def check_list_lengths(cls, v, values: dict) -> List[int]:
        if len(v) != len(values["y_axis"]):
            raise ValueError("Axis lengths do not match")
        return v
