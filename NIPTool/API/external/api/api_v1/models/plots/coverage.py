from typing import List

from pydantic import BaseModel


class CoveragePlotSampleData(BaseModel):
    """validate length of all lists the same"""

    x_axis: List[int]
    y_axis: List[float]
