from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse

from statina.API.external.api.deps import authenticate_user, create_access_token
from statina.API.v2.endpoints.user import credentials_exception
from statina.models.database import User
from statina.models.server.auth import Token

router = APIRouter()


@router.get("/")
def base():
    """Landing page"""
    return JSONResponse("Welcome to Statina!")


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Creating a time delimited access token if the user is found in the database."""

    user: User = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise credentials_exception
    access_token = create_access_token(form_data=form_data, username=user.username)
    return JSONResponse(content=Token(access_token=access_token, token_type="bearer").json())
