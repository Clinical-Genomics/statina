import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from statina.API.external.api.deps import authenticate_user, create_access_token
from statina.config import settings
from statina.models.database import User

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
        response.set_cookie(key="info_type", value="danger")
        response.set_cookie(
            key="user_info",
            value=f"Wrong username or password.",
        )
    else:
        response = RedirectResponse("../batches")
        response.set_cookie(key="token", value=token)
    return response
