import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from NIPTool.API.external.api.deps import (
    authenticate_user,
    create_access_token,
    temp_get_config,
)
from NIPTool.models.server.login import Token
from NIPTool.models.database import User

router = APIRouter()


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), config: dict = Depends(temp_get_config)
) -> Optional[str]:
    """Creating a time delimited access token if the user is found in the database."""

    user: User = authenticate_user(form_data.username, form_data.password)

    if not user:
        return None

    access_token_expires = datetime.timedelta(minutes=config.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

    return create_access_token(
        username=user.username,
        form_data=form_data,
        expires_delta=access_token_expires,
    )


@router.post("/login")
def login(token: Optional[str] = Depends(login_for_access_token)):
    """Redirects back to index, if invalid username or password """

    if not token:
        response = RedirectResponse("../")
    else:
        response = RedirectResponse("../batches")
        response.set_cookie(key="token", value=token)
    return response
