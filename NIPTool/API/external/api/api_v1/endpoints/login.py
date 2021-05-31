import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from NIPTool.API.external.api.deps import authenticate_user, create_access_token
from NIPTool.config import settings
from NIPTool.models.database import User

router = APIRouter()


@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Optional[str]:
    """Creating a time delimited access token if the user is found in the database."""

    user: User = authenticate_user(form_data.username, form_data.password)

    if not user:
        return None

    access_token_expires = datetime.timedelta(minutes=settings.access_token_expire_minutes)

    return create_access_token(
        username=user.username,
        form_data=form_data,
        expires_delta=access_token_expires,
    )


@router.get("/logout")
def logout():
    """Drop token from cookie and redirects back to index"""

    response = RedirectResponse("../")
    response.set_cookie(key="token", value="")
    return response


@router.post("/login")
def login(token: Optional[str] = Depends(login_for_access_token)):
    """Redirects back to index, if invalid username or password"""

    if not token:
        response = RedirectResponse("../")
    else:
        response = RedirectResponse("../batches")
        response.set_cookie(key="token", value=token)
    return response
