from typing import List, Optional

from pydantic import BaseModel, validator


class FetalFraction(BaseModel):
    """validate length of all lists the same"""

    FFY: List[float]
    FFX: List[float]
    FF: Optional[List[float]]
    names: List[str]
    count: int


class Suspected(FetalFraction):
    color: Optional[str] = "#DBA901"
    color_group: Optional[str] = "warning"


class Probable(FetalFraction):
    color: Optional[str] = "#0000FF"
    color_group: Optional[str] = "warning"


class FalseNegative(FetalFraction):
    color: Optional[str] = "#ff6699"
    color_group: Optional[str] = "danger"


class Verified(FetalFraction):
    color: Optional[str] = "#00CC00"
    color_group: Optional[str] = "danger"


class Other(FetalFraction):
    color: Optional[str] = "#603116"
    color_group: Optional[str] = "warning"


class FalsePositive(FetalFraction):
    color: Optional[str] = "#E74C3C"
    color_group: Optional[str] = "success"


class Failed(FetalFraction):
    color_group: Optional[str] = "danger"


class FetalFractionStatus(BaseModel):
    """validate length of all lists the same"""

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
    """validate length of all lists the same"""

    X0: FetalFractionStatus
    XXX: FetalFractionStatus
    XXY: FetalFractionStatus
    XYY: FetalFractionStatus

    class Config:
        validate_assignment = True
