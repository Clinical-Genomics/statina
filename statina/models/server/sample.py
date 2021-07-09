from typing import Literal, Optional

from pydantic import BaseModel, validator

from statina.API.external.constants import (
    SEX_CHROM_ABNORM,
    TRIS_CHROM_ABNORM,
    TRISOMI_TRESHOLDS,
    FF_TRESHOLDS,
)
from statina.models.database import DataBaseSample
from statina.models.server.plots.fetal_fraction_sex import x_get_y


class SampleWarning(BaseModel):
    FF_Formatted: Literal["danger", "default", "warning"]
    Zscore_13: Literal["danger", "default", "warning"]
    Zscore_18: Literal["danger", "default", "warning"]
    Zscore_21: Literal["danger", "default", "warning"]
    FFY: Literal["danger", "default", "warning"]
    X0: Literal["danger", "default", "warning"]
    XXX: Literal["danger", "default", "warning"]
    other: Literal["danger", "default", "warning"]
    XXY: Literal["danger", "default", "warning"]
    XYY: Literal["danger", "default", "warning"]


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
        fetal_fraction_x = values.get("FFX")
        sample_warnings["FF_Formatted"]: str = cls.get_ff_preface_warning(
            fetal_fraction_pf=fetal_fraction_pf, fetal_fraction_y=fetal_fraction_y
        )
        sample_warnings["other"]: str = cls.get_other_warning(
            fetal_fraction_y=fetal_fraction_y, fetal_fraction_x=fetal_fraction_x
        )
        sample_warnings["FFY"]: str = cls.get_ff_y_warning(fetal_fraction_y=fetal_fraction_y)
        sample_warnings["X0"]: str = cls.get_x0_warning(
            fetal_fraction_y=fetal_fraction_y, fetal_fraction_x=fetal_fraction_x
        )
        sample_warnings["XXX"]: str = cls.get_XXX_warning(
            fetal_fraction_y=fetal_fraction_y, fetal_fraction_x=fetal_fraction_x
        )
        sample_warnings["XYY"]: str = cls.get_XYY_warning(
            fetal_fraction_y=fetal_fraction_y, fetal_fraction_x=fetal_fraction_x
        )
        sample_warnings["XXY"]: str = cls.get_XXY_warning(
            fetal_fraction_y=fetal_fraction_y, fetal_fraction_x=fetal_fraction_x
        )

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
    def get_x0_warning(cls, fetal_fraction_y: float, fetal_fraction_x: float) -> str:
        """Get fetal fraction warning based on preset threshold"""

        x_treshold = FF_TRESHOLDS["fetal_fraction_X0"]
        y_treshold = FF_TRESHOLDS["fetal_fraction_y_min"]

        if not (
            isinstance(fetal_fraction_y, (float, int))
            and isinstance(fetal_fraction_x, (float, int))
        ):
            return "default"

        if fetal_fraction_y < y_treshold and fetal_fraction_x > x_treshold:
            return "danger"

        return "default"

    @classmethod
    def get_XXX_warning(cls, fetal_fraction_y: float, fetal_fraction_x: float) -> str:
        """Get fetal fraction warning based on preset threshold"""

        x_treshold = FF_TRESHOLDS["fetal_fraction_XXX"]
        y_treshold = FF_TRESHOLDS["fetal_fraction_y_min"]

        if not (
            isinstance(fetal_fraction_y, (float, int))
            and isinstance(fetal_fraction_x, (float, int))
        ):
            return "default"

        if fetal_fraction_y < y_treshold and fetal_fraction_x < x_treshold:
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

    @classmethod
    def get_other_warning(cls, fetal_fraction_y: float, fetal_fraction_x: float) -> str:
        """Get fetal fraction warning based on preset threshold"""

        k_lower: float = FF_TRESHOLDS["k_lower"]
        m_lower: float = FF_TRESHOLDS["m_lower"]
        y_treshold: float = FF_TRESHOLDS["fetal_fraction_y_min"]

        if not (
            isinstance(fetal_fraction_y, (float, int))
            and isinstance(fetal_fraction_x, (float, int))
        ):
            return "default"

        if y_treshold < fetal_fraction_y <= x_get_y(x=fetal_fraction_x, k=k_lower, m=m_lower):
            return "danger"

        return "default"

    @classmethod
    def get_XXY_warning(cls, fetal_fraction_y: float, fetal_fraction_x: float) -> str:
        """Get fetal fraction warning based on preset threshold"""

        k_upper: float = FF_TRESHOLDS["k_upper"]
        m_upper: float = FF_TRESHOLDS["m_upper"]
        x_treshold: float = FF_TRESHOLDS["fetal_fraction_X0"]

        if not (
            isinstance(fetal_fraction_y, (float, int))
            and isinstance(fetal_fraction_x, (float, int))
        ):
            return "default"

        if fetal_fraction_y > x_get_y(x=fetal_fraction_x, k=k_upper, m=m_upper) and (
            fetal_fraction_x <= x_treshold
        ):
            return "danger"
        return "default"

    @classmethod
    def get_XYY_warning(cls, fetal_fraction_y: float, fetal_fraction_x: float) -> str:
        """Get fetal fraction warning based on preset threshold"""

        k_upper: float = FF_TRESHOLDS["k_upper"]
        m_upper: float = FF_TRESHOLDS["m_upper"]
        x_treshold: float = FF_TRESHOLDS["fetal_fraction_X0"]

        if not (
            isinstance(fetal_fraction_y, (float, int))
            and isinstance(fetal_fraction_x, (float, int))
        ):
            return "default"

        if fetal_fraction_y > x_get_y(x=fetal_fraction_x, k=k_upper, m=m_upper) and (
            fetal_fraction_x > x_treshold
        ):
            return "danger"
        return "default"
