import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from NIPTool.API.external.api.deps import (
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from NIPTool.adapter import NiptAdapter
from NIPTool.config import settings, get_nipt_adapter
from NIPTool.crud.insert import insert_user
from NIPTool.models.database import User
from NIPTool.models.server.load import NewUser

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
    """Redirects back to index, if invalid username or password """

    if not token:
        response = RedirectResponse("../")
    else:
        response = RedirectResponse("../batches")
        response.set_cookie(key="token", value=token)
    return response


@router.post("/add_new_user")
async def add_new_user(request: Request, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """Redirects back to index, if invalid username or password """
    form = await request.form()
    new_user = NewUser(**form)

    user = User(
        **new_user.dict(),
        added=datetime.datetime.now(),
        role="inactive",
        hashed_password=get_password_hash(new_user.password),
    )

    response = RedirectResponse("../new_user")

    try:
        insert_user(adapter=adapter, user=user)
        response.set_cookie(
            key="user_info",
            value=f"An email will be sent to {new_user.email} when your user has been confirmed and activated.",
        )
    except Exception as error:
        response.set_cookie(key="user_info", value=f"{error}")
        pass

    return response
