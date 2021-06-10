from typing import List, Optional

from pydantic import BaseModel, Field, validator


class NCVSamples(BaseModel):
    """Data points for NCV plots.

    Samples within this model will be part of the same series in a plot.

    The x-axis is of type int because:
        NCV plots for a batch have samples on the x-axis.
        NCV plot for a sample have chromosome abnormalities (13 18 21)"""

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


class NCV131821(BaseModel):
    """Model for samples classified as normal chromosome 13, 18, 21.

    Samples are grouped by chromosome."""

    ncv_13: NCVSamples = Field(..., alias="13")
    ncv_18: NCVSamples = Field(..., alias="18")
    ncv_21: NCVSamples = Field(..., alias="21")

    class Config:
        allow_population_by_field_name = True
