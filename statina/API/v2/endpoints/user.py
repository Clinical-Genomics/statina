import datetime
import logging
from typing import List

from fastapi import Depends, Security, APIRouter
from fastapi.encoders import jsonable_encoder
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.responses import JSONResponse

from statina.API.external.api.api_v1.endpoints.login import router
from statina.API.external.api.api_v1.templates.email.confirmation import (
    CONFIRMATION_MESSAGE_TEMPLATE,
)
from statina.API.external.api.deps import get_password_hash
from statina.API.v2.endpoints.login import get_current_active_user
from statina.adapter import StatinaAdapter
from statina.config import get_nipt_adapter, email_settings
from statina.crud.find import find
from statina.crud.insert import insert_user
from statina.exeptions import CredentialsError
from statina.models.database import User
from statina.models.server.new_user import NewUser

from sendmail_container import FormDataRequest
from statina.tools.email import send_email

router = APIRouter()

LOG = logging.getLogger(__name__)


@router.post("/register_user")
async def register_user(
    new_user: NewUser,
    background_tasks: BackgroundTasks,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    user = User(
        **new_user.dict(),
        added=datetime.datetime.now(),
        role="unconfirmed",
        hashed_password=get_password_hash(new_user.password),
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
        return JSONResponse(f"Could not insert, {e}")

    return JSONResponse(content=jsonable_encoder(user))


@router.get("/users")
def users(
    request: Request,
    current_user: User = Security(get_current_active_user, scopes=["admin"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Admin view with table of all users."""
    user_list: List[User] = find.users(adapter=adapter)
    return JSONResponse(
        content=jsonable_encoder(
            {
                "users": user_list,
                "page_id": "users",
            }
        ),
    )
