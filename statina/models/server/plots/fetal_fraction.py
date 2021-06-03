from typing import List, Optional

from pydantic import BaseModel, validator


class FetalFractionSamples(BaseModel):
    """Data points for fetal fraction plots.

    Samples within this model will be part of the same series in a plot."""

    FFY: List[float]
    FFX: List[float]
    FF: Optional[List[float]]
    names: List[str]
    count: int

    @validator("count")
    def check_list_lengths(cls, v, values: dict) -> List[int]:
        for key, plot_list in values.items():
            if plot_list is not None and v != len(plot_list):
                raise ValueError("Axis lengths do not match")
        return v


class Suspected(FetalFractionSamples):
    """Color code for suspected sample"""

    color: Optional[str] = "#DBA901"
    color_group: Optional[str] = "warning"


class Probable(FetalFractionSamples):
    """Color code for probable sample"""

    color: Optional[str] = "#0000FF"
    color_group: Optional[str] = "warning"


class FalseNegative(FetalFractionSamples):
    """Color code for false negative sample"""

    color: Optional[str] = "#ff6699"
    color_group: Optional[str] = "danger"


class Verified(FetalFractionSamples):
    """Color code for verified sample"""

    color: Optional[str] = "#00CC00"
    color_group: Optional[str] = "danger"


class Other(FetalFractionSamples):
    """Color code for other sample"""

    color: Optional[str] = "#603116"
    color_group: Optional[str] = "warning"


class FalsePositive(FetalFractionSamples):
    """Color code for false positive sample"""

    color: Optional[str] = "#E74C3C"
    color_group: Optional[str] = "success"


class Failed(FetalFractionSamples):
    """Color code for failed sample"""

    color_group: Optional[str] = "danger"


class AbNormalityClasses(BaseModel):
    """A sample can be classified with eg probable X0. False Negative XXY, etc.

    This model is for grouping a set of samples by classification of a specific abnormality, eg XXY.

    All classes are optional since, eg, it can be the case that none of the samples in the set are classified as
    False Positive XXY.

    The status_data_ is a dict of all samples in the set, grouped by classification.
    """

    status_data_: dict
    probable: Optional[Probable]
    suspected: Optional[Suspected]
    false_positive: Optional[FalsePositive]
    verified: Optional[Verified]
    false_negative: Optional[FalseNegative]
    other: Optional[Other]
    failed: Optional[Failed]

    @validator("probable", always=True)
    def set_probable(cls, v, values: dict) -> Optional[Probable]:
        status_info: Optional[dict] = values["status_data_"].get("Probable")
        if not status_info:
            return None
        return Probable(**status_info)

    @validator("suspected", always=True)
    def set_suspected(cls, v, values: dict) -> Optional[Suspected]:
        status_info: Optional[dict] = values["status_data_"].get("Suspected")
        if not status_info:
            return None
        return Suspected(**status_info)

    @validator("false_positive", always=True)
    def set_false_positive(cls, v, values: dict) -> Optional[FalsePositive]:
        status_info: Optional[dict] = values["status_data_"].get("False Positive")
        if not status_info:
            return None
        return FalsePositive(**status_info)

    @validator("verified", always=True)
    def set_verified(cls, v, values: dict) -> Optional[Verified]:
        status_info: Optional[dict] = values["status_data_"].get("Verified")
        if not status_info:
            return None
        return Verified(**status_info)

    @validator("false_negative", always=True)
    def set_false_negative(cls, v, values: dict) -> Optional[FalseNegative]:
        status_info: Optional[dict] = values["status_data_"].get("False Negative")
        if not status_info:
            return None
        return FalseNegative(**status_info)

    @validator("other", always=True)
    def set_other(cls, v, values: dict) -> Optional[Other]:
        status_info: Optional[dict] = values["status_data_"].get("Other")
        if not status_info:
            return None
        return Other(**status_info)

    @validator("failed", always=True)
    def set_failed(cls, v, values: dict) -> Optional[Failed]:
        status_info: Optional[dict] = values["status_data_"].get("Failed")
        if not status_info:
            return None
        return Failed(**status_info)


class FetalFractionControlAbNormal(BaseModel):
    """Model for sex chromosome abnormalities.

    This model is only for samples that have ben classified as abnormal sex chromosomes in some sense.

    Samples are grouped by sex chromosome abnormality. Samples within a abnormality group are then grouped by
    abnormality classification, defined by AbNormalityClasses.

    Eg; Each sample in XO have been classified as not normal for sex chromosome abnormality X0.
    The samples within X0 are then grouped by Verified X0, False Positive X0, etc"""

    X0: AbNormalityClasses
    XXX: AbNormalityClasses
    XXY: AbNormalityClasses
    XYY: AbNormalityClasses

    class Config:
        validate_assignment = True
