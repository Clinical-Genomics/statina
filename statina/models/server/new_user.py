from typing import List

from pydantic import BaseModel, EmailStr, validator

from statina.exeptions import MissMatchingPasswordError
from statina.models.database import User


class NewUser(BaseModel):
    email: EmailStr
    username: str
    password_repeated: str
    password: str

    @validator("password", always=True)
    def validate_password(cls, v, values: dict) -> str:
        if v != values["password_repeated"]:
            raise MissMatchingPasswordError
        return v


class PaginatedUserResponse(BaseModel):
    document_count: int
    documents: List[User]
