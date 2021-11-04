from typing import Optional, List

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    email: str
    scopes: Optional[List]
    role: str


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: Optional[List[str]] = []
