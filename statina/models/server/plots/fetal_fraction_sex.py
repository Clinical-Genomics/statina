from dataclasses import dataclass
from typing import List, Optional

import numpy as np
from pydantic import BaseModel, validator

from statina.API.external.constants import SEX_THRESHOLDS


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


class SexChromosomeThresholds:
    """Threshold lines for the Fetal Fraction XY plot"""

    y_min: float = SEX_THRESHOLDS["y_min"]
    y_max: float = SEX_THRESHOLDS["y_max"]
    xx_lower: float = SEX_THRESHOLDS["xx_lower"]
    xx_upper: float = SEX_THRESHOLDS["xx_upper"]
    xy_lowest: float = SEX_THRESHOLDS["xy_lowest"]
    k_upper: float = SEX_THRESHOLDS["k_upper"]
    k_lower: float = SEX_THRESHOLDS["k_lower"]

    def __init__(self, x_min, x_max):
        self.x_min: float = x_min
        self.x_max: float = x_max

    def xy_lower_get_y(self, x: float) -> float:
        k = self.k_lower
        m = self.xy_lowest - k * self.xx_upper
        return k * x + m

    def xy_upper_get_y(self, x: float) -> float:
        k = self.k_upper
        m = self.xy_lowest - k * self.xx_lower
        return k * x + m

    def xy_upper_get_x(self, y: float) -> float:
        k = self.k_upper
        m = self.xy_lowest - k * self.xx_lower
        return (y - m) / k

    def XXY(self) -> ThresholdLine:
        """Returning a threshold line to separate XYY from XXY"""
        x = self.xx_upper
        return ThresholdLine(x=[x, x], y=[self.y_max, self.xy_upper_get_y(x=x)], text=f"x={x}")

    def XY_upper(self) -> ThresholdLine:
        """Returning a threshold line to separate XY from XXY and XYY"""
        return ThresholdLine(
            x=[self.x_max, self.xx_upper],
            y=[
                self.xy_lower_get_y(x=self.x_max),
                self.xy_lower_get_y(x=self.xx_upper),
            ],
            text=f"hej",
        )

    def XY_lower(self) -> ThresholdLine:
        """Returning a threshold line to separate XY from other"""
        return ThresholdLine(
            x=[self.x_max, self.xx_lower],
            y=[
                self.xy_upper_get_y(x=self.x_max),
                self.xy_upper_get_y(x=self.xx_lower),
            ],
            text=f"hej",
        )

    def XY_fetal_fraction_y(self) -> ThresholdLine:
        """Returning a threshold line to separate XY from XX"""
        y = self.xy_lowest
        return ThresholdLine(x=[self.x_min, self.x_max], y=[y, y], text=f"y={y}")

    def XX_upper(self) -> ThresholdLine:
        """Returning a threshold line to separate XX from XXX"""
        x = self.xx_upper

        return ThresholdLine(x=[x, x], y=[self.y_min, self.xy_lowest], text=f"x={x}")

    def XX_lower(self) -> ThresholdLine:
        """Returning a threshold line to separate XX from X0"""
        x = self.xx_lower

        return ThresholdLine(x=[x, x], y=[self.y_min, self.xy_lowest], text=f"x={x}")
