import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sendmail_container import FormDataRequest

from statina.API.external.api.deps import authenticate_user, create_access_token
from statina.adapter import StatinaAdapter
from statina.config import settings, get_nipt_adapter, email_settings
from statina.crud import update
from statina.crud.find import find
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


@router.get("/validate_user")
async def validate_user(
    username: str,
    verification_hex: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    update_user: User = find.user(user_name=username, adapter=adapter)
    response = RedirectResponse("../batches")
    if not update_user:
        response.set_cookie(key="info_type", value="danger")
        response.set_cookie(
            key="user_info",
            value="No such user in the database",
        )
    elif update_user.verification_hex == verification_hex and update_user.role == "unconfirmed":
        try:
            update_user.role = "inactive"
            update.update_user(adapter=adapter, user=update_user)
            email_form = FormDataRequest(
                sender_prefix=email_settings.sender_prefix,
                request_uri=email_settings.mail_uri,
                recipients=email_settings.admin_email,
                mail_title="New user request",
                mail_body=f"User {update_user.username} ({update_user.email}) requested new account <br>"
                f'Follow <a href="{email_settings.website_uri}">link</a> to activate user',
            )
            email_form.submit()
            response.set_cookie(
                key="user_info",
                value="Email confirmed! Your account will be activated after manual review",
            )
        except Exception as e:
            response.set_cookie(key="info_type", value="danger")
            response.set_cookie(
                key="user_info",
                value=f"Backend error ({e.__class__.__name__})! Your account will be activated after manual review",
            )
    return response


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
