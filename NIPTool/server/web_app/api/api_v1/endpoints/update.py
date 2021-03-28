import logging
from typing import Iterable
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.crud import find, update

from NIPTool.models.database import User
from NIPTool.server.web_app.utils import *
from NIPTool.server.web_app.api.deps import get_nipt_adapter, get_current_active_user
from datetime import datetime

router = APIRouter()

LOG = logging.getLogger(__name__)

from pydantic import BaseModel


class Item(BaseModel):
    form_id: str
    sample_id: Optional[str]


@router.post("/update_debugging")
def update_debugging(request: Request, item: Item, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """Update the database"""
    print(item)
    print('hej')
    time_stamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    user = User(username='mayapapaya', email='mayabrandi@123.com', role='RW')
    if user.role != "RW":
        return "", 201

    return RedirectResponse('batches/342712/')


@router.post("/update")
def update(request: Request, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """Update the database"""

    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    user = User(username="mayapapaya", email="mayapapaya@mail.com", role="RW")

    if user.role != "RW":
        return "", 201

    if request.form.get("form_id") == "set_sample_status":
        sample_id: str = request.form["sample_id"]
        sample: Sample = find.sample(sample_id=sample_id)
        # Convert to dict to fetch statuses
        sample_dict: dict = sample.dict()
        for abnormality in CHROM_ABNORM:
            new_abnormality_status: str = request.form[abnormality]
            abnormality_key: str = "_".join(["status", abnormality])
            if sample_dict.get(abnormality_key) != new_abnormality_status:
                LOG.debug(
                    "Updating %s to %s for sample %s",
                    abnormality_key,
                    new_abnormality_status,
                    sample_id,
                )
                sample[abnormality_key] = new_abnormality_status
                sample["status_change_abnormality"] = " ".join([user.name, time_stamp])
        update.sample(adapter=adapter, sample_object=Sample(**sample_dict))

    if request.form.get("form_id") == "set_sample_comment" and request.form.get("comment"):
        sample_id: str = request.form["sample_id"]
        sample: Sample = find.sample(sample_id=sample_id)
        comment: str = request.form.get("comment")
        if comment != sample.comment:
            sample.comment = comment
        update.sample(adapter=adapter, sample_object=sample)

    if request.form.get("button_id") == "Save":
        samples: Iterable[str] = request.form.getlist("samples")
        for sample_id in samples:
            sample: Sample = find.sample(sample_id=sample_id)
            comment: str = request.form.get(f"comment_{sample_id}")
            include: bool = request.form.get(f"include_{sample_id}")
            if comment != sample.comment:
                sample.comment = comment
            if include and not sample.include:
                sample.include = True
                sample.change_include_date = " ".join([user.name, time_stamp])
            elif not include and sample.include:
                sample.include = False
            update.sample(adapter=adapter, sample_object=sample)

    if request.form.get("button_id") == "include all samples":
        samples: Iterable[str] = request.form.getlist("samples")
        for sample_id in samples:
            sample: Sample = find.sample(sample_id=sample_id)
            if sample.include:
                continue
            sample.include = True
            sample.change_include_date = " ".join([user.name, time_stamp])
            update.sample(adapter=adapter, sample_object=sample)

    return RedirectResponse(request.url)
