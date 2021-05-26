from fastapi import APIRouter, Depends, Request

from NIPTool.API.external.api.deps import get_current_user
from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.API.external.utils import *
from NIPTool.config import get_nipt_adapter, templates
from NIPTool.crud import find
from NIPTool.models.database import Batch, User

router = APIRouter()


@router.get("/samples/{sample_id}/")
def sample(
    request: Request,
    sample_id: str,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Get sample with id"""

    sample: Sample = find.sample(sample_id=sample_id, adapter=adapter)
    batch: Batch = find.batch(batch_id=sample.batch_id, adapter=adapter)

    return templates.TemplateResponse(
        "sample/sample.html",
        context=dict(
            request=request,
            current_user=user,
            chrom_abnorm=CHROM_ABNORM,
            sample=sample,
            status_classes=STATUS_CLASSES,
            batch=batch,
            page_id="sample",
        ),
    )


@router.post("/samples/{sample_id}/")
def sample(
    request: Request,
    sample_id: str,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Post sample with id"""

    sample: Sample = find.sample(sample_id=sample_id, adapter=adapter)
    batch: Batch = find.batch(batch_id=sample.batch_id, adapter=adapter)

    return templates.TemplateResponse(
        "sample/sample.html",
        context=dict(
            request=request,
            current_user=user,
            chrom_abnorm=CHROM_ABNORM,
            sample=sample,
            status_classes=STATUS_CLASSES,
            batch=batch,
            page_id="sample",
        ),
    )


@router.get("/samples/{sample_id}/tris")
def sample_tris(
    request: Request,
    sample_id: str,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Sample view with trisomi plot."""
    sample: dict = find.sample(sample_id=sample_id, adapter=adapter).dict()
    batch: Batch = find.batch(batch_id=sample.get("batch_id"), adapter=adapter)
    abnormal_data, data_per_abnormaliy = get_abn_for_samp_tris_plot(adapter=adapter)
    normal_data = get_normal_for_samp_tris_plot(adapter=adapter)
    sample_data = get_sample_for_samp_tris_plot(sample)
    return templates.TemplateResponse(
        "sample/sample_tris.html",
        context=dict(
            request=request,
            current_user=user,
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


@router.post("/samples/{sample_id}/tris")
def sample_tris(
    request: Request,
    sample_id: str,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Sample view with trisomi plot."""
    sample: dict = find.sample(sample_id=sample_id, adapter=adapter).dict()
    batch: Batch = find.batch(batch_id=sample.get("batch_id"), adapter=adapter)
    abnormal_data, data_per_abnormaliy = get_abn_for_samp_tris_plot(adapter=adapter)
    normal_data = get_normal_for_samp_tris_plot(adapter=adapter)
    sample_data = get_sample_for_samp_tris_plot(sample)
    return templates.TemplateResponse(
        "sample/sample_tris.html",
        context=dict(
            request=request,
            current_user=user,
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
