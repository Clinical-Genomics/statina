from typing import List, Optional

from pydantic import BaseModel, Field, validator


class ZscoreSamples(BaseModel):
    """Data points for Zscore plots.

    Samples within this model will be part of the same series in a plot.

    The x-axis is of type int because:
        Zscore plots for a batch have samples on the x-axis.
        Zscore plot for a sample have chromosome abnormalities (13 18 21)"""

    count: Optional[int]
    x_axis: Optional[List[int]]
    names: List[str]
    ncv_values: List[float]

    @validator("ncv_values")
    def check_list_lengths(cls, v, values: dict) -> List[int]:

        if len(v) != len(values["names"]):
            raise ValueError("Axis lengths do not match 1")

        if values["x_axis"] is not None and len(v) != len(values["x_axis"]):
            raise ValueError("Axis lengths do not match 2")

        if values["count"] is not None and len(v) != values["count"]:
            raise ValueError("Axis lengths do not match 3")
        return v

    class Config:
        validate_assignment = True


class Zscore131821(BaseModel):
    """Model for samples classified as normal chromosome 13, 18, 21.

    Samples are grouped by chromosome."""

    chr_13: ZscoreSamples = Field(..., alias="13")
    chr_18: ZscoreSamples = Field(..., alias="18")
    chr_21: ZscoreSamples = Field(..., alias="21")

    class Config:
        allow_population_by_field_name = True
