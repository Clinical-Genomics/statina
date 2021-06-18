from typing import Literal, Optional

from pydantic import BaseModel, validator

from statina.API.external.constants import (
    SEX_CHROM_ABNORM,
    TRIS_CHROM_ABNORM,
    TRISOMI_TRESHOLDS,
    FF_TRESHOLDS,
)
from statina.models.database import DataBaseSample


class SampleWarning(BaseModel):
    FF_Formatted: Literal["danger", "default", "warning"]
    Zscore_13: Literal["danger", "default", "warning"]
    Zscore_18: Literal["danger", "default", "warning"]
    Zscore_21: Literal["danger", "default", "warning"]
    FFY: Literal["danger", "default", "warning"]


class Sample(DataBaseSample):
    warnings: Optional[SampleWarning]
    text_warning: Optional[str]
    status: Optional[str]
    sex: Optional[Literal["XX", "XY"]]

    @validator("Zscore_13")
    def round_zscore_13(cls, v):
        return round(v, 2)

    @validator("Zscore_18")
    def round_zscore_18(cls, v):
        return round(v, 2)

    @validator("Zscore_21")
    def round_zscore_21(cls, v):
        return round(v, 2)

    @validator("Zscore_X")
    def round_zscore_x(cls, v):
        return round(v, 2)

    @validator("FF_Formatted")
    def round_ff(cls, v):
        return round(v, 2)

    @validator("FFX")
    def round_ffx(cls, v):
        return round(v, 2)

    @validator("FFY")
    def round_ffy(cls, v):
        return round(v, 2)

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
        """Get warnings for a sample and return a SampleWarning"""

        sample_warnings = {}
        fetal_fraction_pf = values.get("FF_Formatted")
        fetal_fraction_y = values.get("FFY")
        sample_warnings["FF_Formatted"]: str = cls.get_ff_preface_warning(
            fetal_fraction_pf=fetal_fraction_pf, fetal_fraction_y=fetal_fraction_y
        )
        sample_warnings["FFY"]: str = cls.get_ff_y_warning(fetal_fraction_y=fetal_fraction_y)
        for key in ["Zscore_13", "Zscore_18", "Zscore_21"]:
            z_score = values.get(key)
            sample_warnings[key]: str = cls.get_tris_warning(
                z_score=z_score, fetal_fraction=fetal_fraction_pf
            )
        return SampleWarning(**sample_warnings)

    @validator("text_warning", always=True)
    def set_text_warning(cls, v, values: dict) -> str:
        """Joining the warnings for a sample to a text string"""

        text_warnings = [
            abn for abn, warning in values["warnings"].dict().items() if warning == "danger"
        ]
        return ", ".join(text_warnings)

    @validator("sex", always=True)
    def set_sex(cls, v, values: dict) -> str:
        """Set sex based on fetal fraction Y thresholds"""

        fetal_fraction_y = values.get("FFY")
        return "XY" if fetal_fraction_y >= FF_TRESHOLDS["fetal_fraction_y_min"] else "XX"

    @classmethod
    def get_tris_warning(cls, z_score: float, fetal_fraction: float) -> str:
        """Get automated trisomy warning, based on preset Zscore thresholds"""

        hard_max = TRISOMI_TRESHOLDS["hard_max"]["Zscore"]
        soft_max = TRISOMI_TRESHOLDS["soft_max"]["Zscore"]
        soft_min = TRISOMI_TRESHOLDS["soft_min"]["Zscore"]
        hard_min = TRISOMI_TRESHOLDS["hard_min"]["Zscore"]
        preface = FF_TRESHOLDS["fetal_fraction_preface"]

        if fetal_fraction is None or z_score is None:
            return "default"
        elif fetal_fraction < preface and soft_max < z_score < hard_max:
            return "warning"
        elif hard_min < z_score <= soft_min:
            return "warning"
        elif z_score >= hard_max or z_score <= hard_min:
            return "danger"
        else:
            return "default"

    @classmethod
    def get_ff_y_warning(cls, fetal_fraction_y: float) -> str:
        """Get fetal fraction warning based on preset threshold"""

        y_min = FF_TRESHOLDS["fetal_fraction_y_min"]
        y_max = FF_TRESHOLDS["fetal_fraction_y_max"]

        if not isinstance(fetal_fraction_y, (float, int)):
            return "default"

        if y_min <= fetal_fraction_y < y_max:
            return "danger"

        return "default"

    @classmethod
    def get_ff_preface_warning(cls, fetal_fraction_pf: float, fetal_fraction_y: float) -> str:
        """Get fetal fraction preface warning based on preset threshold"""

        if not (
            isinstance(fetal_fraction_y, (float, int))
            and isinstance(fetal_fraction_pf, (float, int))
        ):
            return "default"
        y_min = FF_TRESHOLDS["fetal_fraction_y_min"]
        pf_min = FF_TRESHOLDS["fetal_fraction_preface"]
        if fetal_fraction_pf < pf_min and fetal_fraction_y < y_min:
            return "danger"
        return "default"
