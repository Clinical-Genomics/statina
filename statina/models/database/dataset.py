from pydantic import BaseModel


class Dataset(BaseModel):
    name: str
    fetal_fraction_preface: float
    fetal_fraction_y_for_trisomy: float
    fetal_fraction_y_max: float
    fetal_fraction_y_min: float
    fetal_fraction_XXX: float
    fetal_fraction_X0: float
    y_axis_min: float
    y_axis_max: float
    k_upper: float
    k_lower: float
    m_lower: float
    m_upper: float
    trisomy_soft_max: float
    trisomy_hard_max: float
    trisomy_hard_min: float
