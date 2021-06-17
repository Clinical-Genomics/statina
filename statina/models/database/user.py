from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    email: EmailStr
    added: datetime
    role: Literal["R", "RW", "inactive", "admin"]
    hashed_password: str
