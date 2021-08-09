from datetime import datetime
from typing import Literal
import secrets

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    email: EmailStr
    added: datetime
    role: Literal["R", "RW", "inactive", "admin", "unconfirmed"]
    hashed_password: str
    verification_hex: str = secrets.token_hex(64)
