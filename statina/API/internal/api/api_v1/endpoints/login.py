import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Header, Security
from fastapi.security import (
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from starlette import status

from statina.API.external.api.deps import authenticate_user, create_access_token, find_user

from statina.config import settings
from jose import JWTError, jwt
from statina.models.database import User
from statina.models.database.user import inactive_roles
from statina.models.server.auth import Token, TokenData

router = APIRouter()
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
LOG = logging.getLogger(__name__)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = find_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.role in inactive_roles:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.get("/users/me/", response_model=TokenData)
async def read_users_me(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
    token_data = TokenData(username=payload.get("sub"))
    return token_data


@router.post("/token", response_model=Token)
def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    """Creating a time delimited access token if the user is found in the database."""

    user: User = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise credentials_exception
    access_token = create_access_token(
        form_data=form_data,
    )
    response.headers["Authorization"] = f"bearer {access_token}"
    return {"access_token": access_token, "token_type": "bearer"}
