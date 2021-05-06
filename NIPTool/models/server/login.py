from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class User(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = None
    added: Optional[datetime] = None
    role: Optional[str] = None
    hashed_password: str
    token: Optional[str]


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []
