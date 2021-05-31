from typing import Dict

from fastapi import APIRouter, Depends, Request

from NIPTool.adapter import NiptAdapter
from NIPTool.API.external.api.deps import get_current_user
from NIPTool.API.external.constants import CHROM_ABNORM, STATUS_CLASSES, STATUS_COLORS
from NIPTool.config import get_nipt_adapter, templates
from NIPTool.crud.find import find
from NIPTool.crud.find.plots.ncv_plot_data import (
    get_abn_for_samp_tris_plot,
    get_normal_for_samp_tris_plot,
    get_sample_for_samp_tris_plot,
)
from NIPTool.models.database import Batch, DataBaseSample, User
from NIPTool.models.server.plots.ncv import NCV131821, NCVSamples

router = APIRouter()


@router.get("/samples/{sample_id}/")
def sample(
    request: Request,
    sample_id: str,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Get sample with id"""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
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

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
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
    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    batch: Batch = find.batch(batch_id=sample.batch_id, adapter=adapter)
    abnormal_data: Dict[str, NCVSamples] = get_abn_for_samp_tris_plot(adapter=adapter)
    normal_data: NCV131821 = get_normal_for_samp_tris_plot(adapter=adapter)
    sample_data: NCVSamples = get_sample_for_samp_tris_plot(sample)
    return templates.TemplateResponse(
        "sample/sample_tris.html",
        context=dict(
            request=request,
            current_user=user,
            normal_data=normal_data.dict(exclude_none=True, by_alias=True),
            abnormal_data=abnormal_data,
            sample_data=sample_data,
            sample=sample.dict(),
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
    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    batch: Batch = find.batch(batch_id=sample.batch_id, adapter=adapter)
    abnormal_data: Dict[str, NCVSamples] = get_abn_for_samp_tris_plot(adapter=adapter)
    normal_data: NCV131821 = get_normal_for_samp_tris_plot(adapter=adapter)
    sample_data: NCVSamples = get_sample_for_samp_tris_plot(sample)
    return templates.TemplateResponse(
        "sample/sample_tris.html",
        context=dict(
            request=request,
            current_user=user,
            normal_data=normal_data,
            abnormal_data=abnormal_data,
            sample_data=sample_data,
            sample=sample.dict(),
            batch=batch,
            status_colors=STATUS_COLORS,
            page_id="sample_tris",
        ),
    )
