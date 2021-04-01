from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.config import get_nipt_adapter
from NIPTool.crud import find
from NIPTool.models.server.login import TokenData, User, UserInDB
from passlib.context import CryptContext


def temp_get_config():
    return {
        "DB_URI": "mongodb://localhost:27030",
        "DB_NAME": "nipt-stage",
        "SECRET_KEY": "97f30d198c86a604f12c22c74077a22cc223009f78fbb8de2065c26cca68e9a5",
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
    }


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/login/token",
    scopes={"me": "Read information about the current user.", "items": "Read items."},
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    config: dict = Depends(temp_get_config),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.get("SECRET_KEY"), algorithms=[config.get("ALGORITHM")])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user: User = find.user(adapter=adapter, user_name=token_data.username)
    if not user:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    adapter = get_nipt_adapter()
    user: User = find.user(adapter=adapter, user_name=username)
    if not user:
        return None
    db_user = UserInDB(**user.dict())
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    configs: dict = temp_get_config()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, configs.get("SECRET_KEY"), algorithm=configs.get("ALGORITHM"))