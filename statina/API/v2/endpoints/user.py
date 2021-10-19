import datetime
import logging
from typing import List, Optional

from fastapi import Depends, Security, APIRouter, Query, Form
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from starlette.background import BackgroundTasks
from starlette.responses import JSONResponse

from statina.API.external.api.api_v1.templates.email.admin_mail import ADMIN_MESSAGE_TEMPLATE
from statina.API.external.api.api_v1.templates.email.confirmation import (
    CONFIRMATION_MESSAGE_TEMPLATE,
)
from statina.API.external.api.deps import get_password_hash
from statina.API.v2.endpoints.login import get_current_active_user
from statina.adapter import StatinaAdapter
from statina.config import get_nipt_adapter, email_settings
from statina.crud import update
from statina.crud.find import find
from statina.crud.insert import insert_user
from statina.exeptions import MissMatchingPasswordError
from statina.models.database import User
import secrets

from sendmail_container import FormDataRequest
from statina.tools.email import send_email

router = APIRouter()

LOG = logging.getLogger(__name__)


@router.post("/register")
async def register_user(
    background_tasks: BackgroundTasks,
    email: EmailStr = Form(...),
    username: str = Form(...),
    password_repeated: str = Form(...),
    password: str = Form(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    if not secrets.compare_digest(password, password_repeated):
        raise MissMatchingPasswordError

    user = User(
        username=username,
        email=email,
        added=datetime.datetime.now(),
        role="unconfirmed",
        hashed_password=get_password_hash(password),
    )
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
    except Exception as e:
        LOG.error(e)
        return JSONResponse(f"Could not register user")

    return JSONResponse(content=user.json(exclude={"role", "hashed_password", "verification_hex"}))


@router.get("/users/")
def users(
    page_size: Optional[int] = Query(5),
    page_num: Optional[int] = Query(0),
    current_user: User = Security(get_current_active_user, scopes=["admin"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Admin view with table of all users."""
    user_list: List[User] = find.users(adapter=adapter, page_size=page_size, page_num=page_num)
    return JSONResponse(content=jsonable_encoder(user_list))


@router.get("/validate_user")
async def validate_user(
    username: str,
    verification_hex: str,
    background_tasks: BackgroundTasks,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    update_user: User = find.user(user_name=username, adapter=adapter)
    if not update_user:
        return JSONResponse(content="No such user", status_code=404)
    if update_user.role != "unconfirmed":
        return JSONResponse(content="User already confirmed", status_code=400)
    if not secrets.compare_digest(update_user.verification_hex, verification_hex):
        return JSONResponse(content="URL is wrong or token has expired", status_code=401)
    try:
        update_user.role = "inactive"
        update.update_user(adapter=adapter, user=update_user)
        email_form = FormDataRequest(
            sender_prefix=email_settings.sender_prefix,
            email_server_alias=email_settings.email_server_alias,
            request_uri=email_settings.mail_uri,
            recipients=email_settings.admin_email,
            mail_title="New user request",
            mail_body=ADMIN_MESSAGE_TEMPLATE.format(
                username=update_user.username,
                user_email=update_user.email,
                website_uri=email_settings.website_uri,
            ),
        )
        background_tasks.add_task(send_email, email_form)
        return JSONResponse(content=f"New status: {update_user.role}", status_code=202)
    except Exception as e:
        LOG.error(e)
        return JSONResponse(content="Server could not verify user", status_code=500)
