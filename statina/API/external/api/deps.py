from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

import statina
from statina.adapter.plugin import StatinaAdapter
from statina.config import get_nipt_adapter, settings
from statina.constants import SCOPES
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
    user: User = statina.crud.find.users.user(adapter=adapter, user_name=username)
    if not user:
        raise CredentialsError(message="User not found in database.")
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> Optional[User]:
    adapter: StatinaAdapter = get_nipt_adapter()
    user: User = statina.crud.find.users.user(adapter=adapter, user_name=username)

    if user and verify_password(password, user.hashed_password):
        return user


def find_user(username: str) -> Optional[User]:
    adapter: StatinaAdapter = get_nipt_adapter()
    user: User = statina.crud.find.users.user(adapter=adapter, user_name=username)

    return user


def get_user_scopes(username: str) -> list:
    user_obj: Optional[User] = find_user(username=username)
    return SCOPES.get(user_obj.role, [])


def create_access_token(
    username: str,
    form_data: OAuth2PasswordRequestForm,
    expires_delta: Optional[timedelta] = timedelta(minutes=15),
) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {
        "sub": form_data.username,
        "scopes": get_user_scopes(username=username),
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
