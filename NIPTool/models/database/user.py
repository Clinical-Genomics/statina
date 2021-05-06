from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = None
    added: Optional[datetime] = None
    role: Optional[str] = None
    hashed_password: Optional[str]
