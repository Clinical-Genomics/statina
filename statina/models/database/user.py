from datetime import datetime
from typing import Literal, Optional
import secrets

from pydantic import BaseModel, EmailStr

inactive_roles = [
    "unconfirmed",
    "inactive",
]


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
