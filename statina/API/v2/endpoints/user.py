import datetime
import logging
import secrets
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Security
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, SecurityScopes, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import EmailStr
from sendmail_container import FormDataRequest
from starlette.background import BackgroundTasks
from starlette.responses import JSONResponse

import statina.crud.find.users
from statina.adapter import StatinaAdapter
from statina.API.external.api.api_v1.templates.email.account_activated import (
    ACTIVATION_MESSAGE_TEMPLATE,
)
from statina.API.external.api.api_v1.templates.email.admin_mail import ADMIN_MESSAGE_TEMPLATE
from statina.API.external.api.api_v1.templates.email.confirmation import (
    CONFIRMATION_MESSAGE_TEMPLATE,
)
from statina.API.external.api.deps import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_user_scopes,
)
from statina.config import email_settings, get_nipt_adapter, settings
from statina.crud import delete, update
from statina.crud.insert import insert_user
from statina.exeptions import credentials_exception, forbidden_access_exception
from statina.models.database import User
from statina.models.database.user import inactive_roles
from statina.models.server.auth import TokenData, Token
from statina.models.server.new_user import PaginatedUserResponse
from statina.tools.email import send_email

router = APIRouter(prefix="/v2")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/v2/token",
    scopes={
        "R": "Read-only access to database",
        "RW": "Read and write access",
        "admin": "Admin permissions",
    },
)


LOG = logging.getLogger(__name__)


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, scopes=payload.get("scopes", []))
    except JWTError:
        raise credentials_exception
    user = statina.crud.find.users.user(user_name=username, adapter=adapter)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise forbidden_access_exception
    return user


async def get_current_active_user(
    current_user: User = Security(get_current_user, scopes=["unconfirmed"])
):
    if current_user:
        return current_user
    raise HTTPException(status_code=401)


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Creating a time delimited access token if the user is found in the database."""

    user: User = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise credentials_exception
    access_token = create_access_token(form_data=form_data, username=user.username)
    return JSONResponse(
        content=jsonable_encoder(
            Token(
                access_token=access_token,
                token_type="bearer",
                username=user.username,
                email=user.email,
                scopes=get_user_scopes(username=user.username),
                role=user.role,
            )
        )
    )


@router.post(
    "/user/register",
    response_model=User,
    response_model_exclude={"hashed_password", "verification_hex"},
)
async def register_user(
    background_tasks: BackgroundTasks,
    email: EmailStr = Form(...),
    username: str = Form(...),
    password_repeated: str = Form(...),
    password: str = Form(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):

    if statina.crud.find.users.user(user_name=username, adapter=adapter):
        return JSONResponse(f"Username {username} already taken!", status_code=409)
    elif statina.crud.find.users.user(email=email, adapter=adapter):
        return JSONResponse(f"Email {email} already in use!", status_code=409)
    if not secrets.compare_digest(password, password_repeated):
        return JSONResponse(content="Password mismatch!", status_code=400)

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
        return JSONResponse(f"Could not register user", status_code=500)

    return JSONResponse(
        content=jsonable_encoder(
            user.dict(exclude={"hashed_password", "verification_hex"}),
            by_alias=False,
        )
    )


@router.get("/users", response_model=PaginatedUserResponse)
def users(
    page_size: Optional[int] = Query(5),
    page_num: Optional[int] = Query(0),
    role: Literal["", "admin", "unconfirmed", "inactive", "R", "RW"] = Query(""),
    query_string: Optional[str] = Query(""),
    sort_key: Literal["added", "username", "email"] = Query("added"),
    sort_direction: Literal["ascending", "descending"] = Query("ascending"),
    current_user: User = Security(get_current_active_user, scopes=["admin"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Admin view with table of all users."""
    user_list: List[User] = statina.crud.find.users.query_users(
        adapter=adapter,
        page_size=page_size,
        query_string=query_string,
        role=role,
        sort_key=sort_key,
        sort_direction=sort_direction,
        page_num=page_num,
    )
    document_count = statina.crud.find.users.count_query_users(
        adapter=adapter, query_string=query_string, role=role
    )
    return JSONResponse(
        content=jsonable_encoder(
            PaginatedUserResponse(document_count=document_count, documents=user_list),
            by_alias=False,
        ),
        status_code=200,
    )


@router.patch("/user/{username}/validate")
async def validate_user_email(
    username: str,
    background_tasks: BackgroundTasks,
    verification_hex: str = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    update_user: User = statina.crud.find.users.user(user_name=username, adapter=adapter)
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


@router.put("/user/{username}/role")
async def update_user_role(
    username: str,
    background_tasks: BackgroundTasks,
    role: Literal[
        "unconfirmed",
        "inactive",
        "R",
        "RW",
        "admin",
    ] = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["admin"]),
):
    update_user: User = statina.crud.find.users.user(user_name=username, adapter=adapter)
    old_role = update_user.role
    update_user.role = role
    update.update_user(adapter=adapter, user=update_user)
    if old_role in inactive_roles and role not in inactive_roles:
        email_form = FormDataRequest(
            sender_prefix=email_settings.sender_prefix,
            email_server_alias=email_settings.email_server_alias,
            request_uri=email_settings.mail_uri,
            recipients=update_user.email,
            mail_title="Your account has been activated",
            mail_body=ACTIVATION_MESSAGE_TEMPLATE.format(
                website_uri=email_settings.website_uri, username=update_user.username
            ),
        )
        background_tasks.add_task(send_email, email_form)
    return JSONResponse(content="User updated", status_code=202)


@router.get(
    "/user/me", response_model=User, response_model_exclude={"hashed_password", "verification_hex"}
)
async def read_users_me(
    current_user: User = Security(get_current_active_user, scopes=["unconfirmed"])
):
    return JSONResponse(
        content=jsonable_encoder(
            current_user.dict(exclude={"hashed_password", "verification_hex"}),
            by_alias=False,
        ),
        status_code=200,
    )


@router.delete("/user/{username}")
async def delete_user(
    username: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["admin"]),
):
    delete.delete_user(adapter=adapter, username=username)
    return JSONResponse(content=f"User {username} deleted", status_code=201)
