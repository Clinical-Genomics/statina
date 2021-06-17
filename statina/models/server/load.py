from typing import Optional

from pydantic import BaseModel, EmailStr
from typing_extensions import Literal


class BatchRequestBody(BaseModel):
    result_file: str
    multiqc_report: Optional[str]
    segmental_calls: Optional[str]


class UserRequestBody(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: Literal["R", "RW", "admin"]
