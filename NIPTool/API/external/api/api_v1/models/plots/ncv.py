from typing import List
from pydantic import BaseModel


class NCVSamples(BaseModel):
    """validate length of all lists the same"""

    values: List[float]
    names: List[str]
    count: int
