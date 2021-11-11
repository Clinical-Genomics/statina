from typing import Literal, Optional, List

from pydantic import BaseModel, validator, Field

from statina.API.external.constants import (
    SEX_CHROM_ABNORM,
    TRIS_CHROM_ABNORM,
    TRISOMI_TRESHOLDS,
    FF_TRESHOLDS,
)
from statina.constants import sample_status_options
from statina.models.database import DataBaseSample
from statina.models.server.plots.fetal_fraction_sex import x_get_y


class SampleWarning(BaseModel):
    fetal_fraction_preface: Literal["danger", "default", "warning"]
    fetal_fraction_y: Literal["danger", "default", "warning"]
    z_score_13: Literal["danger", "default", "warning"]
    z_score_18: Literal["danger", "default", "warning"]
    z_score_21: Literal["danger", "default", "warning"]
    x0: Literal["danger", "default", "warning"]
    xxx: Literal["danger", "default", "warning"]
    other: Literal["danger", "default", "warning"]
    xxy: Literal["danger", "default", "warning"]
    xyy: Literal["danger", "default", "warning"]


class Status(BaseModel):
    status: sample_status_options
    edited: str


class ZScore(BaseModel):
    z_score_13: str = Field(..., alias="13")
    z_score_18: str = Field(..., alias="18")
    z_score_21: str = Field(..., alias="21")
    z_score_x: str = Field(..., alias="x")

    class Config:
        allow_population_by_field_name = True


class FetalFraction(BaseModel):
    x: str
    y: str
    preface: str


class Include(BaseModel):
    include: Optional[bool] = False
    edited: Optional[str] = ""


class Statuses(BaseModel):
    status_13: Status = Field(..., alias="13")
    status_18: Status = Field(..., alias="18")
    status_21: Status = Field(..., alias="21")
    status_x0: Status = Field(..., alias="x0")
    status_xxx: Status = Field(..., alias="xxx")
    status_xxy: Status = Field(..., alias="xxy")
    status_xyy: Status = Field(..., alias="xyy")

    class Config:
        allow_population_by_field_name = True


class SampleValidator(DataBaseSample):
    warnings: Optional[SampleWarning]
    status_string: Optional[str]
    status: Optional[Statuses]
    fetal_fraction: Optional[FetalFraction]
    z_score: Optional[ZScore]
    included: Optional[Include]
    sex: Optional[Literal["XX", "XY"]]
    sample_type: str = Field(..., alias="SampleType")
    qc_flag: str = Field(..., alias="QCFlag")
    cnv_segment: Optional[str] = Field(..., alias="CNVSegment")
    text_warning: Optional[str]

    @validator("warnings", always=True)
    def set_warnings(cls, v, values: dict) -> SampleWarning:
        """Get warnings for a sample and return a SampleWarning"""

        sample_warnings = {}
        fetal_fraction_pf = values.get("FF_Formatted")
        fetal_fraction_y = values.get("FFY")
        fetal_fraction_x = values.get("FFX")
        sample_warnings["fetal_fraction_preface"]: str = cls.get_ff_preface_warning(
            fetal_fraction_pf=fetal_fraction_pf, fetal_fraction_y=fetal_fraction_y
        )
        sample_warnings["other"]: str = cls.get_other_warning(
            fetal_fraction_y=fetal_fraction_y, fetal_fraction_x=fetal_fraction_x
        )
        sample_warnings["fetal_fraction_y"]: str = cls.get_ff_y_warning(
            fetal_fraction_y=fetal_fraction_y
        )
        sample_warnings["x0"]: str = cls.get_x0_warning(
            fetal_fraction_y=fetal_fraction_y, fetal_fraction_x=fetal_fraction_x
        )
        sample_warnings["xxx"]: str = cls.get_XXX_warning(
            fetal_fraction_y=fetal_fraction_y, fetal_fraction_x=fetal_fraction_x
        )
        sample_warnings["xyy"]: str = cls.get_XYY_warning(
            fetal_fraction_y=fetal_fraction_y, fetal_fraction_x=fetal_fraction_x
        )
        sample_warnings["xxy"]: str = cls.get_XXY_warning(
            fetal_fraction_y=fetal_fraction_y, fetal_fraction_x=fetal_fraction_x
        )
        sample_warnings["z_score_13"]: str = cls.get_tris_warning(
            z_score=values.get("Zscore_13"), fetal_fraction=fetal_fraction_pf
        )
        sample_warnings["z_score_18"]: str = cls.get_tris_warning(
            z_score=values.get("Zscore_18"), fetal_fraction=fetal_fraction_pf
        )
        sample_warnings["z_score_21"]: str = cls.get_tris_warning(
            z_score=values.get("Zscore_21"), fetal_fraction=fetal_fraction_pf
        )
        return SampleWarning(**sample_warnings)

    @validator("fetal_fraction", always=True)
    def set_fetal_fraction(cls, v, values: dict) -> FetalFraction:

        return FetalFraction(
            x=round(values["FFX"], 2),
            y=round(values["FFY"], 2),
            preface=round(values["FF_Formatted"], 2),
        )

    @validator("z_score", always=True)
    def set_z_score(cls, v, values: dict) -> ZScore:

        return ZScore(
            z_score_13=round(values["Zscore_13"], 2),
            z_score_18=round(values["Zscore_18"], 2),
            z_score_21=round(values["Zscore_21"], 2),
            z_score_x=round(values["Zscore_X"], 2),
        )

    @validator("status_string", always=True)
    def set_status_string(cls, v, values: dict) -> str:

        status_list = []
        for key in TRIS_CHROM_ABNORM + SEX_CHROM_ABNORM:
            status = values.get(f"status_{key}")
            if status and status != "Normal":
                status_list.append(" ".join([status, key]))
        return ", ".join(status_list)

    @validator("status", always=True)
    def set_status(cls, v, values: dict) -> Statuses:

        statuses_dict = {
            f"status_{key.lower()}": Status(
                status=values.get(f"status_{key}"),
                edited=values.get(f"status_change_{key}"),
            )
            for key in TRIS_CHROM_ABNORM + SEX_CHROM_ABNORM
        }

        return Statuses(**statuses_dict)

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

    @validator("included", always=True)
    def set_include(cls, v, values: dict) -> Optional[Include]:
        return Include(include=values["include"], edited=values["change_include_date"])

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

    class Config:
        allow_population_by_field_name = True


class Sample(BaseModel):
    sample_type: str
    qc_flag: str
    cnv_segment: Optional[str]
    comment: str
    sample_id: str
    batch_id: str
    warnings: Optional[SampleWarning]
    text_warning: str
    sex: Optional[str]
    sequencing_date: Optional[str]
    status: Statuses
    included: Include
    z_score: ZScore
    fetal_fraction: FetalFraction

    class Config:
        allow_population_by_field_name = True


class PaginatedSampleResponse(BaseModel):
    document_count: int
    documents: List[Sample]
