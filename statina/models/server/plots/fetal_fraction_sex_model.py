from typing import List, Optional

import numpy as np
from pydantic import BaseModel, validator, root_validator


class ThresholdLine(BaseModel):
    x: List[float]
    y: List[float]
    text: str
    text_position: Optional[List[float]]

    @validator("text_position", always=True)
    def set_text_position(cls, v, values: dict) -> List[np.ndarray]:
        """ """

        return [np.mean(values["x"]), np.mean(values["y"])]


class SexChromosomeThresholds(BaseModel):
    y_min: float = -1
    y_max: float = 20
    x_min: float
    x_max: float
    xx_lower: float = 2
    xx_upper: float = 4
    xy_lowest: float = 0.5
    XXY: Optional[ThresholdLine]
    XY_upper: Optional[ThresholdLine]
    XY_lower: Optional[ThresholdLine]
    XY_horisontal: Optional[ThresholdLine]
    XX_upper: Optional[ThresholdLine]
    XX_lower: Optional[ThresholdLine]

    @classmethod
    def straight_line_get_y(cls, x: float, m: float, k: float) -> float:
        return k * x + m

    @classmethod
    def xy_lower_get_y(cls, x: float) -> float:
        k = 1.51
        m = 0.5 - k * 4
        return k * x + m

    @classmethod
    def xy_upper_get_y(cls, x: float) -> float:
        k = 1.49
        m = 0.5 - k * 2
        return k * x + m

    @classmethod
    def xy_upper_get_x(cls, y: float) -> float:
        k = 1.49
        m = 0.5 - k * 2
        return (y - m) / k

    @validator("XXY", always=True)
    def set_XXY(cls, v, values: dict) -> ThresholdLine:
        """ """
        x = values["xx_upper"]

        return ThresholdLine(x=[x, x], y=[values["y_max"], cls.xy_upper_get_y(x=x)], text=f"x={x}")

    @validator("XY_lower", always=True)
    def set_XY_upper(cls, v, values: dict) -> ThresholdLine:
        """ """
        return ThresholdLine(
            x=[values["x_max"], values["xx_upper"]],
            y=[
                cls.xy_lower_get_y(x=values["x_max"]),
                cls.xy_lower_get_y(x=values["xx_upper"]),
            ],
            text=f"hej",
        )

    @validator("XY_upper", always=True)
    def set_XY_lower(cls, v, values: dict) -> ThresholdLine:
        """ """
        return ThresholdLine(
            x=[values["x_max"], values["xx_lower"]],
            y=[
                cls.xy_upper_get_y(x=values["x_max"]),
                cls.xy_upper_get_y(x=values["xx_lower"]),
            ],
            text=f"hej",
        )

    @validator("XY_horisontal", always=True)
    def set_XY_horisontal(cls, v, values: dict) -> ThresholdLine:
        """ """
        y = values["xy_lowest"]
        return ThresholdLine(x=[values["x_min"], values["x_max"]], y=[y, y], text=f"y={y}")

    @validator("XX_upper", always=True)
    def set_XX_upper(cls, v, values: dict) -> ThresholdLine:
        """ """
        x = values["xx_upper"]

        return ThresholdLine(x=[x, x], y=[values["y_min"], values["xy_lowest"]], text=f"x={x}")

    @validator("XX_lower", always=True)
    def set_XX_lower(cls, v, values: dict) -> ThresholdLine:
        """ """
        x = values["xx_lower"]

        return ThresholdLine(x=[x, x], y=[values["y_min"], values["xy_lowest"]], text=f"x={x}")
