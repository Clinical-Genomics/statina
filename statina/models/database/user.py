from datetime import datetime
from typing import Literal
import secrets

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    email: EmailStr
    added: datetime
    role: Literal[
        "unconfirmed",
        "inactive",
        "R",
        "RW",
        "admin",
    ]
    hashed_password: str
    verification_hex: str = secrets.token_urlsafe(64)
