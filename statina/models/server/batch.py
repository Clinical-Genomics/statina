from typing import List, Optional

from pydantic import BaseModel, Field, validator

from statina.models.database import DatabaseBatch


class Median(BaseModel):
    median_13: Optional[float] = Field(..., alias="13")
    median_18: Optional[float] = Field(..., alias="18")
    median_21: Optional[float] = Field(..., alias="21")
    median_x: Optional[float] = Field(..., alias="x")
    median_y: Optional[float] = Field(..., alias="y")

    class Config:
        allow_population_by_field_name = True


class Stdev(BaseModel):
    stdev_13: Optional[float] = Field(..., alias="13")
    stdev_18: Optional[float] = Field(..., alias="18")
    stdev_21: Optional[float] = Field(..., alias="21")
    stdev_x: Optional[float] = Field(..., alias="x")
    stdev_y: Optional[float] = Field(..., alias="y")

    class Config:
        allow_population_by_field_name = True


class BatchValidator(DatabaseBatch):
    flowcell: Optional[str] = Field(None, alias="Flowcell")
    sequencing_date: Optional[str] = Field(None, alias="SequencingDate")
    median: Optional[Median]
    stdev: Optional[Stdev]

    @validator("median", always=True)
    def set_median(cls, v, values: dict) -> Median:
        return Median(
            median_13=round(values["Median_13"], 2),
            median_18=round(values["Median_18"], 2),
            median_21=round(values["Median_21"], 2),
            median_x=round(values["Median_X"], 2),
            median_y=round(values["Median_Y"], 2),
        )

    @validator("stdev", always=True)
    def set_stdev(cls, v, values: dict) -> Stdev:
        return Stdev(
            stdev_13=round(values["Stdev_13"], 2),
            stdev_18=round(values["Stdev_18"], 2),
            stdev_21=round(values["Stdev_21"], 2),
            stdev_x=round(values["Stdev_X"], 2),
            stdev_y=round(values["Stdev_Y"], 2),
        )


class Batch(BaseModel):
    batch_id: str
    result_file: Optional[str]
    multiqc_report: Optional[str]
    segmental_calls: Optional[str]
    flowcell: Optional[str]
    sequencing_date: Optional[str]
    comment: Optional[str]
    median: Median
    stdev: Stdev

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True


class PaginatedBatchResponse(BaseModel):
    document_count: int
    documents: List[Batch]
