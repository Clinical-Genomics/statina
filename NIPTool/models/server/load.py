from typing import Optional

from pydantic import BaseModel, EmailStr, validator
from typing_extensions import Literal

from NIPTool.exeptions import MissMatchingUserNamesError


class BatchRequestBody(BaseModel):
    result_file: str
    multiqc_report: Optional[str]
    segmental_calls: Optional[str]


class UserRequestBody(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: Literal["R", "RW"]


class NewUser(BaseModel):
    email: EmailStr
    username: str
    password_repeted: str
    password: str

    @validator("password", always=True)
    def validate_password(cls, v, values: dict) -> str:
        if v != values["password_repeted"]:
            raise MissMatchingUserNamesError
        return v
