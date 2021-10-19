import datetime
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, SecurityScopes
from starlette import status

from statina.API.external.api.deps import authenticate_user, create_access_token, find_user

from statina.config import settings
from jose import JWTError, jwt
from statina.models.database import User
from statina.models.database.user import inactive_roles
from statina.models.server.auth import Token, TokenData

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "R": "Read-only access to database",
        "RW": "Read and write access",
        "admin": "Admin permissions",
    },
)
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

LOG = logging.getLogger(__name__)


async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
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
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Security(get_current_user, scopes=["R"])):
    if current_user.role in inactive_roles:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Security(get_current_active_user, scopes=["R"])):
    return current_user


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Creating a time delimited access token if the user is found in the database."""

    user: User = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise credentials_exception
    access_token = create_access_token(form_data=form_data, username=user.username)
    return {"access_token": access_token, "token_type": "bearer"}
