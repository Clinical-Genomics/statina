from typing import List, Optional
from pydantic import BaseModel, Field, validator


class NCVSamples(BaseModel):
    """validate length of all lists the same"""

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


class NCVStatus(BaseModel):
    suspected: Optional[NCVSamples] = Field(alias="Suspected")
    probable: Optional[NCVSamples] = Field(alias="Probable")
    verified: Optional[NCVSamples] = Field(alias="Verified")
    false_positive: Optional[NCVSamples] = Field(alias="False Positive")
    false_negative: Optional[NCVSamples] = Field(alias="False Negative")
    other: Optional[NCVSamples] = Field(alias="Other")
    failed: Optional[NCVSamples] = Field(alias="Failed")


class NCV131821(BaseModel):
    ncv_13: NCVSamples = Field(..., alias="13")
    ncv_18: NCVSamples = Field(..., alias="18")
    ncv_21: NCVSamples = Field(..., alias="21")

    class Config:
        allow_population_by_field_name = True
