import logging
from datetime import datetime
from typing import Iterable, Literal, Optional, List
import secrets

from fastapi import APIRouter, Depends, Request, BackgroundTasks, Security, Form, Query
from fastapi.responses import RedirectResponse
from sendmail_container import FormDataRequest
from starlette.datastructures import FormData
from starlette.responses import JSONResponse

from statina.API.external.api.api_v1.templates.email.account_activated import (
    ACTIVATION_MESSAGE_TEMPLATE,
)
from statina.API.external.api.api_v1.templates.email.admin_mail import ADMIN_MESSAGE_TEMPLATE
from statina.API.v2.endpoints.login import get_current_active_user
from statina.adapter import StatinaAdapter
from statina.API.external.constants import CHROM_ABNORM, STATUSES
from statina.config import get_nipt_adapter, email_settings
from statina.crud import update
from statina.crud.delete import delete_batch
from statina.crud.find import find
from statina.models.database import DataBaseSample, User, Batch
from statina.tools.email import send_email

router = APIRouter()

LOG = logging.getLogger(__name__)


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


@router.put("/user/{username}")
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
    update_user: User = find.user(user_name=username, adapter=adapter)
    old_role = update_user.role
    update_user.role = role
    update.update_user(adapter=adapter, user=update_user)
    if old_role in ["inactive", "unconfirmed"] and role not in ["inactive", "unconfirmed"]:
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


@router.delete("/batch/{batch_id}")
async def batch_delete(
    batch_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["admin"]),
):
    await delete_batch(adapter=adapter, batch_id=batch_id)
    return JSONResponse(content=f"Deleted batch {batch_id}", status_code=200)


@router.put("/sample/{sample_id}/13")
async def set_sample_status_13(
    sample_id: str,
    status: Literal[
        "Suspected", "Verified", "Probable", "False Negative", "Other", "Failed"
    ] = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.status_13 = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_13 = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/18")
async def set_sample_status_18(
    sample_id: str,
    status: Literal[
        "Suspected", "Verified", "Probable", "False Negative", "Other", "Failed"
    ] = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.status_18 = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_18 = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/21")
async def set_sample_status_21(
    sample_id: str,
    status: Literal[
        "Suspected", "Verified", "Probable", "False Negative", "Other", "Failed"
    ] = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.status_21 = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_21 = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/X0")
async def set_sample_status_x0(
    sample_id: str,
    status: Literal[
        "Suspected", "Verified", "Probable", "False Negative", "Other", "Failed"
    ] = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.status_X0 = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_X0 = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/XXY")
async def set_sample_status_xxy(
    sample_id: str,
    status: Literal[
        "Suspected", "Verified", "Probable", "False Negative", "Other", "Failed"
    ] = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.status_XXY = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_XXY = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/XXX")
async def set_sample_status_xxx(
    sample_id: str,
    status: Literal[
        "Suspected", "Verified", "Probable", "False Negative", "Other", "Failed"
    ] = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.status_XXX = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_XXX = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/XYY")
async def set_sample_status_xyy(
    sample_id: str,
    status: Literal[
        "Suspected", "Verified", "Probable", "False Negative", "Other", "Failed"
    ] = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.status_XYY = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_XYY = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/batch/{batch_id}/comment")
async def batch_update_comment(
    batch_id: str,
    comment: Optional[str] = Form(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update batch comment"""

    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)
    batch.comment = comment
    update.update_batch(adapter=adapter, batch=batch)

    return JSONResponse(content="Batch comment updated", status_code=202)


@router.put("/sample/{sample_id}/comment")
async def sample_comment(
    sample_id: str,
    comment: Optional[str] = Form(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update sample comment"""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.comment = comment
    update.sample(adapter=adapter, sample=sample)

    return JSONResponse(content="Sample comment updated", status_code=200)


@router.put("/sample/{sample_id}/include")
async def sample_include(
    sample_id: str,
    include: bool = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update sample comment"""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.include = include
    update.sample(adapter=adapter, sample=sample)

    return JSONResponse(content="Sample comment updated", status_code=200)


@router.put("/batch/{batch_id}/include_samples")
async def include_samples(
    batch_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update include status and comment for samples in batch"""
    samples: List[DataBaseSample] = find.batch_samples(adapter=adapter, batch_id=batch_id)
    for sample in samples:
        sample.include = True
        sample.change_include_date = (
            f'{current_user.username} {datetime.now().strftime("%Y/%m/%d %H:%M:%S")}'
        )
        update.sample(adapter=adapter, sample=sample)

    return JSONResponse(content="All samples included in batch plots", status_code=200)
