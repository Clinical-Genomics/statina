from typing import Optional

from pydantic import BaseModel, EmailStr


class BatchRequestBody(BaseModel):
    result_file: str
    multiqc_report: Optional[str]
    segmental_calls: Optional[str]


class UserRequestBody(BaseModel):
    email: EmailStr
    username: str
    role: str
