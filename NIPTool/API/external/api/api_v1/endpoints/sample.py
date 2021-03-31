from fastapi import APIRouter, Depends, Request
from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.crud import find
from NIPTool.models.database import User
from NIPTool.API.external.utils import *
from NIPTool.API.external.api.deps import get_nipt_adapter

from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/samples/{sample_id}/")
def sample(request: Request, sample_id: str, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """Sample view with sample information."""

    sample: dict = find.sample(sample_id=sample_id, adapter=adapter).dict()
    batch = find.batch(batch_id=sample.get("batch_id"), adapter=adapter)

    return templates.TemplateResponse(
        "sample/sample.html",
        context=dict(
            request=request,
            current_user=User(username="mayapapaya", email="mayabrandi@123.com", role="RW"),
            chrom_abnorm=CHROM_ABNORM,
            sample=sample,
            status_classes=STATUS_CLASSES,
            batch=batch,
            page_id="sample",
        ),
    )


@router.post("/samples/{sample_id}/")
def sample(request: Request, sample_id: str, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """Sample view with sample information."""

    sample: dict = find.sample(sample_id=sample_id, adapter=adapter).dict()
    batch = find.batch(batch_id=sample.get("batch_id"), adapter=adapter)

    return templates.TemplateResponse(
        "sample/sample.html",
        context=dict(
            request=request,
            current_user=User(username="mayapapaya", email="mayabrandi@123.com", role="RW"),
            chrom_abnorm=CHROM_ABNORM,
            sample=sample,
            status_classes=STATUS_CLASSES,
            batch=batch,
            page_id="sample",
        ),
    )


@router.get("/samples/{sample_id}/tris")
def sample_tris(request: Request, sample_id: str, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """Sample view with trisomi plot."""
    sample: dict = find.sample(sample_id=sample_id, adapter=adapter).dict()
    batch = find.batch(batch_id=sample.get("batch_id"), adapter=adapter)
    abnormal_data, data_per_abnormaliy = get_abn_for_samp_tris_plot(adapter=adapter)
    normal_data = get_normal_for_samp_tris_plot(adapter=adapter)
    sample_data = get_sample_for_samp_tris_plot(sample)
    return templates.TemplateResponse(
        "sample/sample_tris.html",
        context=dict(
            request=request,
            current_user=User(username="mayapapaya", email="mayabrandi@123.com", role="RW"),
            tris_abn=data_per_abnormaliy,
            normal_data=normal_data,
            abnormal_data=abnormal_data,
            sample_data=sample_data,
            sample=sample,
            batch=batch,
            status_colors=STATUS_COLORS,
            page_id="sample_tris",
        ),
    )
