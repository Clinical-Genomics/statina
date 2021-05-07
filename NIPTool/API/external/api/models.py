from typing import Literal, List, Optional

from pydantic import BaseModel, validator, condecimal, confloat

from NIPTool.API.external.constants import (
    TRIS_CHROM_ABNORM,
    SEX_CHROM_ABNORM,
    FF_TRESHOLD,
    TRISOMI_TRESHOLDS,
)
from NIPTool.models.database import DataBaseSample


class SampleWarning(BaseModel):
    FF_Formatted: Literal["danger", "default", "warning"]
    Zscore_13: Literal["danger", "default", "warning"]
    Zscore_18: Literal["danger", "default", "warning"]
    Zscore_21: Literal["danger", "default", "warning"]


class CoveragePlotSampleData(BaseModel):
    """validate length of all lists the same"""

    x_axis: List[int]
    y_axis: List[float]


class FetalFraction(BaseModel):
    """validate length of all lists the same"""

    FFY: List[float]
    FFX: List[float]
    FF: Optional[List[float]]
    names: List[str]
    count: int

    @validator("count")
    def get_count(cls, v, values):
        return len(values.get("FFY"))


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


class Sample(DataBaseSample):
    warnings: Optional[SampleWarning]
    text_warning: Optional[str]
    status: Optional[str]

    @validator("status", always=True)
    def set_status(cls, v, values: dict) -> str:

        status_list = []
        for key in TRIS_CHROM_ABNORM + SEX_CHROM_ABNORM:
            status = values.get(f"status_{key}")
            if status and status != "Normal":
                status_list.append(" ".join([status, key]))
        return ", ".join(status_list)

    @validator("warnings", always=True)
    def set_warnings(cls, v, values: dict) -> SampleWarning:

        """"""

        sample_warnings = {}
        fetal_fraction = values.get("FF_Formatted")
        sample_warnings["FF_Formatted"]: str = cls.get_ff_warning(fetal_fraction=fetal_fraction)
        for key in ["Zscore_13", "Zscore_18", "Zscore_21"]:
            z_score = values.get(key)
            sample_warnings[key]: str = cls.get_tris_warning(
                z_score=z_score, fetal_fraction=fetal_fraction
            )

        return SampleWarning(**sample_warnings)

    @validator("text_warning", always=True)
    def set_text_warning(cls, v, values: dict) -> str:

        """"""

        return ""

    @classmethod
    def get_tris_warning(cls, z_score: float, fetal_fraction: float) -> str:
        """Get automated trisomy warning, based on preset Zscore thresholds"""

        if fetal_fraction is None or z_score is None:
            return "default"

        if fetal_fraction <= 5:
            soft_max = TRISOMI_TRESHOLDS["soft_max_ff"]["NCV"]
        else:
            soft_max = TRISOMI_TRESHOLDS["soft_max"]["NCV"]
        hard_min = TRISOMI_TRESHOLDS["hard_min"]["NCV"]
        hard_max = TRISOMI_TRESHOLDS["hard_max"]["NCV"]
        soft_min = TRISOMI_TRESHOLDS["soft_min"]["NCV"]

        if (soft_max <= z_score < hard_max) or (hard_min < z_score <= soft_min):
            return "warning"
        elif (z_score >= hard_max) or (z_score <= hard_min):
            return "danger"
        else:
            return "default"

    @classmethod
    def get_ff_warning(cls, fetal_fraction: float) -> str:
        """Get fetal fraction warning based on preset threshold"""

        if isinstance(fetal_fraction, float) and fetal_fraction <= FF_TRESHOLD:
            return "danger"

        return "default"
