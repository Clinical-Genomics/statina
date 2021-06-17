from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from statina.adapter.plugin import StatinaAdapter
from statina.config import get_nipt_adapter, settings
from statina.crud.find import find
from statina.exeptions import CredentialsError
from statina.models.database import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_current_user(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
) -> User:
    """Decoding user from token stored in cookies."""
    try:
        payload = jwt.decode(
            request.cookies.get("token"),
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        username: str = payload.get("sub")
        if username is None:
            raise CredentialsError(message="Could not validate credentials")
    except JWTError:
        raise CredentialsError(message="Could not validate credentials")
    user: User = find.user(adapter=adapter, user_name=username)
    if not user:
        raise CredentialsError(message="User not found in database.")
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> Optional[User]:
    adapter: StatinaAdapter = get_nipt_adapter()
    user: User = find.user(adapter=adapter, user_name=username)

    if not user:
        return None
    if user.role == "inactive":
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(
    username: str, form_data: OAuth2PasswordRequestForm, expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = {"sub": username, "scopes": form_data.scopes}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
