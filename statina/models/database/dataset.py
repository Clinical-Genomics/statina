from pydantic import BaseModel


class Dataset(BaseModel):
    name: str
    fetal_fraction_preface: float = 4
    fetal_fraction_y_for_trisomy: float = 4
    fetal_fraction_y_max: float = 3
    fetal_fraction_y_min: float = 0.6
    fetal_fraction_XXX: float = -1
    fetal_fraction_X0: float = 3.4
    y_axis_min: float = -1
    y_axis_max: float = 20
    k_upper: float = 0.9809
    k_lower: float = 0.9799
    m_lower: float = -4.3987
    m_upper: float = 6.5958
    trisomy_soft_max: float = 3
    trisomy_hard_max: float = 4
    trisomy_hard_min: float = -8
