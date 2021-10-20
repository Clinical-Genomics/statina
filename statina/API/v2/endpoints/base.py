from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse
from statina.API.external.api.deps import authenticate_user, create_access_token

from statina.API.v2.endpoints.user import credentials_exception
from statina.models.database import User
from statina.models.server.auth import Token

router = APIRouter(prefix="/v2")


@router.get("/")
def base():
    """Landing page"""
    return JSONResponse("Welcome to Statina!")
