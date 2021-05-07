from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from NIPTool.config import get_nipt_adapter
from NIPTool.crud import find
from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.exeptions import CredentialsError

from NIPTool.models.server.login import TokenData
from NIPTool.models.database import User
from passlib.context import CryptContext


def temp_get_config():
    return {
        "DB_URI": "mongodb://localhost:27030",
        "DB_NAME": "nipt-stage",
        "SECRET_KEY": "97f30d198c86a604f12c22c74077a22cc223009f78fbb8de2065c26cca68e9a5",
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": 10,
    }


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_current_user(
    request: Request,
    config: dict = Depends(temp_get_config),
    adapter: NiptAdapter = Depends(get_nipt_adapter),
) -> User:
    """Decoding user from token stored in cookies."""

    try:
        payload = jwt.decode(
            request.cookies.get("token"),
            config.get("SECRET_KEY"),
            algorithms=[config.get("ALGORITHM")],
        )
        username: str = payload.get("sub")
        if username is None:
            raise CredentialsError(message="Could not validate credentials")
        token_data = TokenData(username=username)
    except JWTError:
        raise CredentialsError(message="Could not validate credentials")
    user: User = find.user(adapter=adapter, user_name=token_data.username)
    if not user:
        raise CredentialsError(message="User not found in database.")
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> Optional[User]:
    adapter: NiptAdapter = get_nipt_adapter()
    user: User = find.user(adapter=adapter, user_name=username)

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(
    username: str, form_data: OAuth2PasswordRequestForm, expires_delta: Optional[timedelta] = None
) -> str:
    configs: dict = temp_get_config()
    to_encode = {"sub": username, "scopes": form_data.scopes}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, configs.get("SECRET_KEY"), algorithm=configs.get("ALGORITHM"))
