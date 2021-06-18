import datetime
import smtplib
import ssl
from email.message import EmailMessage
from typing import List

from fastapi import Depends
from pydantic import EmailStr
from starlette.requests import Request
from starlette.responses import RedirectResponse

from statina.API.external.api.api_v1.endpoints.login import router
from statina.API.external.api.deps import get_password_hash, get_current_user
from statina.adapter import StatinaAdapter
from statina.config import get_nipt_adapter, templates
from statina.crud.find import find
from statina.crud.insert import insert_user
from statina.exeptions import EmailNotSentError, CredentialsError
from statina.models.database import User
from statina.models.server.new_user import NewUserRequestEmail, NewUser


def send_mail(user: str, email: EmailStr):
    """Email handler. Sending new user request email to admin"""

    try:
        email_info = NewUserRequestEmail(message=user, user_email=email)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            email_info.smtp_server, email_info.sll_port, context=context
        ) as server:
            server.login(email_info.sender_email, email_info.sender_password)
            msg = EmailMessage()
            msg.set_content(email_info.message)
            msg["Subject"] = email_info.subject
            msg["From"] = email_info.sender_email
            msg["To"] = email_info.admin_email
            server.send_message(msg)
    except:
        raise EmailNotSentError(
            message=f"Your user has been created, but not activated. Please send an email to "
            f"admin and ask for permission."
        )


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
        send_mail(
            user=new_user.username, email=new_user.email
        )  # if thisone fails, the error is not picked up!?!?!
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
