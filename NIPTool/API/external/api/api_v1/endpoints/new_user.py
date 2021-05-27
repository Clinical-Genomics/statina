import datetime
import smtplib
import ssl
from email.message import EmailMessage

from fastapi import Depends
from pydantic import EmailStr
from starlette.requests import Request
from starlette.responses import RedirectResponse

from NIPTool.API.external.api.api_v1.endpoints.login import router
from NIPTool.API.external.api.deps import get_password_hash
from NIPTool.adapter import NiptAdapter
from NIPTool.config import get_nipt_adapter
from NIPTool.crud.insert import insert_user
from NIPTool.exeptions import EmailNotSentError
from NIPTool.models.database import User
from NIPTool.models.server.new_user import NewUserRequestEmail, NewUser


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
        send_mail(
            user=new_user.username, email=new_user.email
        )  # if thisone fails, the error is not picked up!?!?!
        response.set_cookie(
            key="user_info",
            value=f"Your user account has been created and an email has been sent to the NIPTool admin. "
            f"They will send an email to {new_user.email} when your user has been confirmed and activated.",
        )
    except Exception as error:
        response.set_cookie(key="user_info", value=f"{error}")
        pass

    return response
