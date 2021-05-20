from typing import List, Optional
from pydantic import BaseModel, Field


class NCVSamples(BaseModel):
    """validate length of all lists the same"""

    ncv_values: List[float]
    names: List[str]
    count: Optional[int]
    x_axis: Optional[List[int]]

    class Config:
        validate_assignment = True


class NCVStatus(BaseModel):
    suspected: Optional[NCVSamples] = Field(alias="Susspected")
    probable: Optional[NCVSamples] = Field(alias="Probable")
    verified: Optional[NCVSamples] = Field(alias="Verified")
    false_positive: Optional[NCVSamples] = Field(alias="False Posetive")
    false_negative: Optional[NCVSamples] = Field(alias="False Negative")
    other: Optional[NCVSamples] = Field(alias="Other")
    failed: Optional[NCVSamples] = Field(alias="Failed")


class NCV131821(BaseModel):
    ncv_13: NCVSamples = Field(..., alias="13")
    ncv_18: NCVSamples = Field(..., alias="18")
    ncv_21: NCVSamples = Field(..., alias="21")

    class Config:
        allow_population_by_field_name = True
