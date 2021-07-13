from dataclasses import dataclass
from typing import List, Optional

import numpy as np
from pydantic import BaseModel, validator

from statina.API.external.constants import FF_TRESHOLDS


class ThresholdLine(BaseModel):
    """Model for treshold lines for plots."""

    x: List[float]
    y: List[float]
    text: str
    text_position: Optional[List[float]]

    @validator("text_position", always=True)
    def set_text_position(cls, v, values: dict) -> List[np.ndarray]:
        """ """
        return [np.mean(values["x"]), np.mean(values["y"])]


def x_get_y(x: float, k: float, m: float) -> float:
    return k * x + m


def y_get_x(y: float, k: float, m: float) -> float:
    return (y - m) / k


class SexChromosomeThresholds:
    """Threshold lines for the Fetal Fraction XY plot"""

    y_axis_min: float = FF_TRESHOLDS["y_axis_min"]
    y_axis_max: float = FF_TRESHOLDS["y_axis_max"]
    xx_lower: float = FF_TRESHOLDS["fetal_fraction_XXX"]
    xx_upper: float = FF_TRESHOLDS["fetal_fraction_X0"]
    xy_lowest: float = FF_TRESHOLDS["fetal_fraction_y_min"]
    k_upper: float = FF_TRESHOLDS["k_upper"]
    k_lower: float = FF_TRESHOLDS["k_lower"]
    m_lower: float = FF_TRESHOLDS["m_lower"]
    m_upper: float = FF_TRESHOLDS["m_upper"]

    def __init__(self, x_min, x_max):
        self.x_min: float = x_min
        self.x_max: float = x_max

    def XXY(self) -> ThresholdLine:
        """Returning a threshold line to separate XYY from XXY"""
        x = self.xx_upper
        return ThresholdLine(
            x=[x, x],
            y=[
                x_get_y(x=x, k=self.k_upper, m=self.m_upper),
                x_get_y(x=self.x_max, k=self.k_upper, m=self.m_upper),
            ],
            text=f"x = {x}",
        )

    def XY_lower(self) -> ThresholdLine:
        """Returning a threshold line to separate XY from other"""
        return ThresholdLine(
            x=[y_get_x(y=self.xy_lowest, k=self.k_lower, m=self.m_lower), self.x_max],
            y=[
                self.xy_lowest,
                x_get_y(x=self.x_max, k=self.k_lower, m=self.m_lower),
            ],
            text=f"y = {self.k_lower}x + {self.m_lower}",
        )

    def XY_upper(self) -> ThresholdLine:
        """Returning a threshold line to separate XY from XXY and XYY"""
        return ThresholdLine(
            x=[y_get_x(y=self.xy_lowest, k=self.k_upper, m=self.m_upper), self.x_max],
            y=[
                self.xy_lowest,
                x_get_y(x=self.x_max, k=self.k_upper, m=self.m_upper),
            ],
            text=f"y = {self.k_upper}x + {self.m_upper}",
        )

    def XY_fetal_fraction_y(self) -> ThresholdLine:
        """Returning a threshold line to separate XY from XX"""
        y = self.xy_lowest
        return ThresholdLine(x=[self.x_min, self.x_max], y=[y, y], text=f"y = {y}")

    def XX_upper(self) -> ThresholdLine:
        """Returning a threshold line to separate XX from XXX"""
        x = self.xx_upper

        return ThresholdLine(x=[x, x], y=[self.y_axis_min, self.xy_lowest], text=f"x = {x}")

    def XX_lower(self) -> ThresholdLine:
        """Returning a threshold line to separate XX from X0"""
        x = self.xx_lower

        return ThresholdLine(x=[x, x], y=[self.y_axis_min, self.xy_lowest], text=f"x = {x}")
