import logging
from datetime import datetime
from typing import Iterable

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from starlette.datastructures import FormData

from statina.adapter import StatinaAdapter
from statina.API.external.api.deps import get_current_user
from statina.API.external.constants import CHROM_ABNORM
from statina.config import get_nipt_adapter
from statina.crud import update
from statina.crud.delete import delete_batches
from statina.crud.find import find
from statina.models.database import DataBaseSample, User

router = APIRouter()

LOG = logging.getLogger(__name__)


@router.post("/delete_batch")
async def delete_batch(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    form = await request.form()
    if user.role != "admin":  ## should be admin. Need fix stuf before
        return RedirectResponse(request.headers.get("referer"))
    batches: Iterable[str] = form.getlist("delete")
    delete_batches(adapter=adapter, batches=batches)
    return RedirectResponse(request.headers.get("referer"))


@router.post("/set_sample_status")
async def set_sample_status(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    form = await request.form()

    if user.role not in ["RW", "admin"]:
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
        sample[f"status_change_{abnormality}"] = f"{user.username} {time_stamp}"

    update.sample(adapter=adapter, sample=DataBaseSample(**sample))
    return RedirectResponse(request.headers.get("referer"))


@router.post("/sample_comment")
async def sample_comment(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Update sample comment"""

    form = await request.form()

    if user.role not in ["RW", "admin"]:
        return RedirectResponse(request.headers.get("referer"))

    sample_id: str = form["sample_id"]
    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    comment: str = form.get("comment")
    if comment != sample.comment:
        sample.comment = comment
        update.sample(adapter=adapter, sample=sample)

    return RedirectResponse(request.headers.get("referer"))


@router.post("/include_samples")
async def include_samples(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Update include status and comment for samples in batch"""

    form = await request.form()

    if user.role not in ["RW", "admin"]:
        return RedirectResponse(request.headers.get("referer"))

    button_id = form.get("button_id")
    samples: Iterable[str] = form.getlist("samples")
    if button_id == "include all samples":
        include_all_samples(samples=samples, adapter=adapter, user=user)
    elif button_id == "Save":
        save_samples(samples=samples, form=form, adapter=adapter, user=user)

    return RedirectResponse(request.headers.get("referer"))


def save_samples(samples: Iterable[str], form: FormData, adapter: StatinaAdapter, user: User):
    """Function to update sample.comment and sample.include."""

    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    for sample_id in samples:
        sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
        comment: str = form.get(f"comment_{sample_id}")
        include: bool = form.get(f"include_{sample_id}")
        if comment != sample.comment:
            sample.comment = comment
        if include and not sample.include:
            sample.include = True
            sample.change_include_date = f"{user.username} {time_stamp}"
        elif not include and sample.include:
            sample.include = False
        update.sample(adapter=adapter, sample=sample)


def include_all_samples(samples: Iterable[str], adapter: StatinaAdapter, user: User):
    """Function to set sample.include=True for all samples."""

    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    for sample_id in samples:
        sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
        if sample.include:
            continue
        sample.include = True
        sample.change_include_date = f"{user.username} {time_stamp}"
        update.sample(adapter=adapter, sample=sample)
