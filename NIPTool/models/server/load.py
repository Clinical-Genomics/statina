from typing import Optional

from pydantic import BaseModel


class BatchRequestBody(BaseModel):
    result_file: str
    multiqc_report: Optional[str]
    segmental_calls: Optional[str]


class UserRequestBody(BaseModel):
    email: str
    username: str
    role: str
