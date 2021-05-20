from typing import List, Optional
from pydantic import BaseModel, Field


class NCVSamples(BaseModel):
    """validate length of all lists the same"""

    values: List[float]
    names: List[str]
    count: int


class NCVStatus(BaseModel):
    suspected: Optional[NCVSamples] = Field(alias="Susspected")
    probable: Optional[NCVSamples] = Field(alias="Probable")
    verified: Optional[NCVSamples] = Field(alias="Verified")
    false_positive: Optional[NCVSamples] = Field(alias="False Posetive")
    false_negative: Optional[NCVSamples] = Field(alias="False Negative")
    other: Optional[NCVSamples] = Field(alias="Other")
    failed: Optional[NCVSamples] = Field(alias="Failed")


class NCVControl(BaseModel):
    ncv_13: Optional[NCVStatus] = Field(..., alias="13")
    ncv_18: Optional[NCVStatus] = Field(..., alias="18")
    ncv_21: Optional[NCVStatus] = Field(..., alias="21")
