from typing import Literal, Optional

from pydantic import BaseModel, Field

status_options = Literal[
    "Probable",
    "Suspected",
    "False Positive",
    "Verified",
    "False Negative",
    "Other",
    "Failed",
    "Normal",
]


class DataBaseSample(BaseModel):
    sample_id: str = Field(..., alias="SampleID")
    batch_id: str = Field(..., alias="SampleProject")
    SampleType: Optional[str] = ""
    Description: Optional[str]
    Flowcell: Optional[str]
    Index1: Optional[str]
    Index2: Optional[str]
    Library_nM: Optional[float]
    QCFlag: Optional[str] = ""
    Zscore_13: Optional[float]
    Zscore_18: Optional[float]
    Zscore_21: Optional[float]
    Zscore_X: Optional[float]
    MappedReads: Optional[int]
    GC_Dropout: Optional[float]
    AT_Dropout: Optional[float]
    Chr1_Ratio: Optional[float]
    Chr2_Ratio: Optional[float]
    Chr3_Ratio: Optional[float]
    Chr4_Ratio: Optional[float]
    Chr5_Ratio: Optional[float]
    Chr6_Ratio: Optional[float]
    Chr7_Ratio: Optional[float]
    Chr8_Ratio: Optional[float]
    Chr9_Ratio: Optional[float]
    Chr10_Ratio: Optional[float]
    Chr11_Ratio: Optional[float]
    Chr12_Ratio: Optional[float]
    Chr13_Ratio: Optional[float]
    Chr18_Ratio: Optional[float]
    Chr21_Ratio: Optional[float]
    ChrX_Ratio: Optional[float]
    ChrY_Ratio: Optional[float]
    Chr14_Ratio: Optional[float]
    Chr15_Ratio: Optional[float]
    Chr16_Ratio: Optional[float]
    Chr17_Ratio: Optional[float]
    Chr19_Ratio: Optional[float]
    Chr20_Ratio: Optional[float]
    Chr22_Ratio: Optional[float]
    Chr1: Optional[int]
    Chr2: Optional[int]
    Chr3: Optional[int]
    Chr4: Optional[int]
    Chr5: Optional[int]
    Chr6: Optional[int]
    Chr7: Optional[int]
    Chr8: Optional[int]
    Chr9: Optional[int]
    Chr10: Optional[int]
    Chr11: Optional[int]
    Chr12: Optional[int]
    Chr13: Optional[int]
    Chr14: Optional[int]
    Chr15: Optional[int]
    Chr16: Optional[int]
    Chr17: Optional[int]
    Chr18: Optional[int]
    Chr19: Optional[int]
    Chr20: Optional[int]
    Chr21: Optional[int]
    Chr22: Optional[int]
    ChrX: Optional[int]
    ChrY: Optional[int]
    FF_Formatted: Optional[float] = Field(..., alias="Fetal Fraction Preface")
    FFY: Optional[float]
    FFX: Optional[float]
    DuplicationRate: Optional[float]
    Bin2BinVariance: Optional[float]
    UnfilteredCNVcalls: Optional[int]
    CNVSegment: Optional[str]
    segmental_calls: Optional[str]
    include: Optional[bool]
    change_include_date: Optional[str] = ""
    comment: Optional[str] = ""
    status_13: Optional[status_options] = "Normal"
    status_18: Optional[status_options] = "Normal"
    status_21: Optional[status_options] = "Normal"
    status_X0: Optional[status_options] = "Normal"
    status_XXX: Optional[status_options] = "Normal"
    status_XXY: Optional[status_options] = "Normal"
    status_XYY: Optional[status_options] = "Normal"
    status_change_13: Optional[str] = ""
    status_change_18: Optional[str] = ""
    status_change_21: Optional[str] = ""
    status_change_X0: Optional[str] = ""
    status_change_XXX: Optional[str] = ""
    status_change_XXY: Optional[str] = ""
    status_change_XYY: Optional[str] = ""

    class Config:
        allow_population_by_field_name = True
