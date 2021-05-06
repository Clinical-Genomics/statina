import logging
from datetime import datetime
from typing import Iterable

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from NIPTool.API.external.api.deps import get_current_user
from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.API.external.utils import *
from NIPTool.config import get_nipt_adapter
from NIPTool.crud import update
from NIPTool.models.database import User
from starlette.datastructures import FormData

router = APIRouter()

LOG = logging.getLogger(__name__)

USER = User(username="mayapapaya", email="mayapapaya@mail.com", role="RW")


@router.post("/set_sample_status")
async def set_sample_status(
    request: Request,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user=Depends(get_current_user),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    form = await request.form()

    if USER.role != "RW":
        return RedirectResponse(request.headers.get("referer"))

    sample_id: str = form["sample_id"]
    sample: dict = find.sample(sample_id=sample_id, adapter=adapter).dict()

    for abnormality in CHROM_ABNORM:
        new_abnormality_status: str = form[abnormality]
        abnormality_key: str = f"status_{abnormality}"
        if sample.get(abnormality_key) == new_abnormality_status:
            continue

        LOG.debug(
            "Updating %s to %s for sample %s",
            abnormality_key,
            new_abnormality_status,
            sample_id,
        )
        time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        sample[abnormality_key] = new_abnormality_status
        sample[f"status_change_{abnormality}"] = f"{USER.username} {time_stamp}"

    update.sample(adapter=adapter, sample=Sample(**sample))
    return RedirectResponse(request.headers.get("referer"))


@router.post("/sample_comment")
async def sample_comment(
    request: Request,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user=Depends(get_current_user),
):
    """Update sample comment"""

    form = await request.form()

    if USER.role != "RW":
        return RedirectResponse(request.headers.get("referer"))

    sample_id: str = form["sample_id"]
    sample: Sample = find.sample(sample_id=sample_id, adapter=adapter)
    comment: str = form.get("comment")
    if comment != sample.comment:
        sample.comment = comment
        update.sample(adapter=adapter, sample=sample)

    return RedirectResponse(request.headers.get("referer"))


@router.post("/include_samples")
async def include_samples(
    request: Request,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Update include status and comment for samples in batch"""

    form = await request.form()

    if USER.role != "RW":
        return RedirectResponse(request.headers.get("referer"))

    button_id = form.get("button_id")
    samples: Iterable[str] = form.getlist("samples")
    if button_id == "include all samples":
        include_all_samples(samples=samples, adapter=adapter)
    elif button_id == "Save":
        save_samples(samples=samples, form=form, adapter=adapter)

    return RedirectResponse(request.headers.get("referer"))


def save_samples(samples: Iterable[str], form: FormData, adapter: NiptAdapter):
    """Function to update sample.comment and sample.include."""

    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    for sample_id in samples:
        sample: Sample = find.sample(sample_id=sample_id, adapter=adapter)
        comment: str = form.get(f"comment_{sample_id}")
        include: bool = form.get(f"include_{sample_id}")
        if comment != sample.comment:
            sample.comment = comment
        if include and not sample.include:
            sample.include = True
            sample.change_include_date = f"{USER.username} {time_stamp}"
        elif not include and sample.include:
            sample.include = False
        update.sample(adapter=adapter, sample=sample)


def include_all_samples(samples: Iterable[str], adapter: NiptAdapter):
    """Function to set sample.include=True for all samples."""

    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    for sample_id in samples:
        sample: Sample = find.sample(sample_id=sample_id, adapter=adapter)
        if sample.include:
            continue
        sample.include = True
        sample.change_include_date = f"{USER.username} {time_stamp}"
        update.sample(adapter=adapter, sample=sample)
