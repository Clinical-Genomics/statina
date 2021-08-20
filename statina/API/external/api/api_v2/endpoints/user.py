import datetime
from typing import List

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse

from statina.API.external.api.api_v1.endpoints.login import router
from statina.API.external.api.api_v1.templates.email.confirmation import (
    CONFIRMATION_MESSAGE_TEMPLATE,
)
from statina.API.external.api.deps import get_password_hash, get_current_user
from statina.adapter import StatinaAdapter
from statina.config import get_nipt_adapter, templates, email_settings
from statina.crud.find import find
from statina.crud.insert import insert_user
from statina.exeptions import CredentialsError
from statina.models.database import User
from statina.models.server.new_user import NewUser

from sendmail_container import FormDataRequest
from statina.tools.email import send_email

user = {}


@router.post("/add_new_user")
async def add_new_user(
    request: Request,
    background_tasks: BackgroundTasks,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Redirects back to index, if invalid username or password"""
    form = await request.form()
    new_user = NewUser(**form)

    user = User(
        **new_user.dict(),
        added=datetime.datetime.now(),
        role="unconfirmed",
        hashed_password=get_password_hash(new_user.password),
    )

    response = RedirectResponse("new_user")

    try:
        insert_user(adapter=adapter, user=user)
        confirmation_link = (
            f"{email_settings.website_uri}/validate_user/"
            f"?username={user.username}&verification_hex={user.verification_hex}"
        )
        email_form = FormDataRequest(
            sender_prefix=email_settings.sender_prefix,
            email_server_alias=email_settings.email_server_alias,
            request_uri=email_settings.mail_uri,
            recipients=user.email,
            mail_title="Verify your email",
            mail_body=CONFIRMATION_MESSAGE_TEMPLATE.format(
                website_uri=email_settings.website_uri,
                confirmation_link=confirmation_link,
                username=user.username,
            ),
        )
        background_tasks.add_task(send_email, email_form)
        response.set_cookie(key="info_type", value="success")
        response.set_cookie(
            key="user_info",
            value=f"Your user account has been created and a validation email has been sent to your email address.",
        )

    except Exception as error:
        response.set_cookie(key="info_type", value="danger")
        response.set_cookie(
            key="user_info", value=f"Error occurred when creating new user. Please try again later"
        )
        pass

    return response


@router.get("/new_user")
def new_user(request: Request):
    """Log in view."""
    return templates.TemplateResponse(
        "new_user.html", context={"request": request, "current_user": ""}
    )


@router.post("/new_user")
def new_user(request: Request):
    """Log in view."""
    return JSONResponse(
        content=jsonable_encoder(
            {
                "current_user": "",
                "info_type": request.cookies.get("info_type"),
                "user_info": request.cookies.get("user_info"),
            }
        ),
    )


@router.get("/users")
def users(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Admin view with table of all users."""
    if user.role != "admin":
        raise CredentialsError(message="Only admin users can access the users page")

    user_list: List[User] = find.users(adapter=adapter)
    return JSONResponse(
        content=jsonable_encoder(
            {
                "users": user_list,
                "page_id": "users",
                "current_user": user,
            }
        ),
    )


@router.post("/users")
def users(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Admin view with table of all users."""
    if user.role != "admin":
        CredentialsError(message="Only admin users can access the users page")

    user_list: List[User] = find.users(adapter=adapter)
    return JSONResponse(
        content=jsonable_encoder(
            {
                "users": user_list,
                "page_id": "users",
                "current_user": user,
            }
        ),
    )
