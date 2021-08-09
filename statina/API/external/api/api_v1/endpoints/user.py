import datetime
from email.message import EmailMessage
from typing import List

from fastapi import Depends
from starlette.requests import Request
from starlette.responses import RedirectResponse

from statina.API.external.api.api_v1.endpoints.login import router
from statina.API.external.api.deps import get_password_hash, get_current_user
from statina.adapter import StatinaAdapter
from statina.config import get_nipt_adapter, templates, email_settings
from statina.crud.find import find
from statina.crud.insert import insert_user
from statina.exeptions import CredentialsError
from statina.models.database import User
from statina.models.server.new_user import NewUser

from sendmail_container import FormDataRequest


@router.post("/add_new_user")
async def add_new_user(request: Request, adapter: StatinaAdapter = Depends(get_nipt_adapter)):
    """Redirects back to index, if invalid username or password"""
    form = await request.form()
    new_user = NewUser(**form)

    user = User(
        **new_user.dict(),
        added=datetime.datetime.now(),
        role="inactive",
        hashed_password=get_password_hash(new_user.password),
    )

    response = RedirectResponse("new_user")

    try:
        insert_user(adapter=adapter, user=user)
        email_form = FormDataRequest(
            sender_prefix=email_settings.sender_prefix,
            request_uri=email_settings.mail_uri,
            recipients=email_settings.admin_email,
            mail_title="New user request",
            mail_body=f"User {new_user.username} ({new_user.email}) requested new account <br>"
            f'Follow <a href="{email_settings.website_uri}">link</a> to activate user',
        )
        email_form.submit()
        response.set_cookie(key="info_type", value="success")
        response.set_cookie(
            key="user_info",
            value=f"Your user account has been created and an email has been sent to the Statina admin. "
            f"They will send an email to {new_user.email} when your user has been confirmed and activated.",
        )

    except Exception as error:
        response.set_cookie(key="info_type", value="danger")
        response.set_cookie(key="user_info", value=f"{error}")
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
    return templates.TemplateResponse(
        "new_user.html",
        context={
            "request": request,
            "current_user": "",
            "info_type": request.cookies.get("info_type"),
            "user_info": request.cookies.get("user_info"),
        },
    )


@router.get("/users")
def users(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Admin view with table of all users."""
    if user.role != "admin":
        raise CredentialsError(message="Only admin users can access the users page")

    user_list: List[User] = find.users(adapter=adapter)
    return templates.TemplateResponse(
        "users.html",
        context={
            "request": request,
            "users": user_list,
            "page_id": "users",
            "current_user": user,
        },
    )


@router.post("/users")
def users(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Admin view with table of all users."""
    if user.role != "admin":
        CredentialsError(message="Only admin users can access the users page")

    user_list: List[User] = find.users(adapter=adapter)
    return templates.TemplateResponse(
        "users.html",
        context={
            "request": request,
            "users": user_list,
            "page_id": "users",
            "current_user": user,
        },
    )
