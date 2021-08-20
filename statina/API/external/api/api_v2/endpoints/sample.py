from typing import Dict, List

from fastapi import APIRouter, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from statina.adapter import StatinaAdapter
from statina.API.external.api.deps import get_current_user
from statina.API.external.constants import CHROM_ABNORM, STATUS_CLASSES, STATUS_COLORS
from statina.config import get_nipt_adapter
from statina.crud.find import find
from statina.crud.find.plots.zscore_plot_data import (
    get_abn_for_samp_tris_plot,
    get_normal_for_samp_tris_plot,
    get_sample_for_samp_tris_plot,
)
from statina.models.database import Batch, DataBaseSample, User
from statina.models.server.plots.ncv import Zscore131821, ZscoreSamples
from statina.models.server.sample import Sample

user = {}
router = APIRouter()


@router.get("/samples/")
def samples(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Get sample with id"""
    samples: List[DataBaseSample] = find.samples(adapter=adapter)
    return JSONResponse(
        content=jsonable_encoder(
            dict(
                current_user=user,
                sample_info=[Sample(**sample.dict()) for sample in samples],
                page_id="samples",
            )
        ),
    )


@router.get("/samples/{sample_id}/")
def sample(
    request: Request,
    sample_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Get sample with id"""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    batch: Batch = find.batch(batch_id=sample.batch_id, adapter=adapter)
    return JSONResponse(
        content=jsonable_encoder(
            dict(
                current_user=user,
                chrom_abnorm=CHROM_ABNORM,
                sample=Sample(**sample.dict()),
                status_classes=STATUS_CLASSES,
                batch=batch,
                page_id="sample",
            )
        ),
    )


@router.post("/samples/{sample_id}/")
def sample(
    request: Request,
    sample_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Post sample with id"""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    batch: Batch = find.batch(batch_id=sample.batch_id, adapter=adapter)
    return JSONResponse(
        content=jsonable_encoder(
            dict(
                current_user=user,
                chrom_abnorm=CHROM_ABNORM,
                sample=Sample(**sample.dict()),
                status_classes=STATUS_CLASSES,
                batch=batch,
                page_id="sample",
            )
        ),
    )


@router.get("/samples/{sample_id}/tris")
def sample_tris(
    request: Request,
    sample_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Sample view with trisomi plot."""
    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    batch: Batch = find.batch(batch_id=sample.batch_id, adapter=adapter)
    abnormal_data: Dict[str, ZscoreSamples] = get_abn_for_samp_tris_plot(adapter=adapter)
    normal_data: Zscore131821 = get_normal_for_samp_tris_plot(adapter=adapter)
    sample_data: ZscoreSamples = get_sample_for_samp_tris_plot(sample)
    return JSONResponse(
        content=jsonable_encoder(
            dict(
                current_user=user,
                normal_data=normal_data.dict(exclude_none=True, by_alias=True),
                abnormal_data=abnormal_data,
                sample_data=sample_data,
                sample=Sample(**sample.dict()),
                batch=batch,
                status_colors=STATUS_COLORS,
                page_id="sample_tris",
            )
        ),
    )


@router.post("/samples/{sample_id}/tris")
def sample_tris(
    request: Request,
    sample_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Sample view with trisomi plot."""
    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    batch: Batch = find.batch(batch_id=sample.batch_id, adapter=adapter)
    abnormal_data: Dict[str, ZscoreSamples] = get_abn_for_samp_tris_plot(adapter=adapter)
    normal_data: Zscore131821 = get_normal_for_samp_tris_plot(adapter=adapter)
    sample_data: ZscoreSamples = get_sample_for_samp_tris_plot(sample)
    return JSONResponse(
        content=jsonable_encoder(
            dict(
                current_user=user,
                normal_data=normal_data,
                abnormal_data=abnormal_data,
                sample_data=sample_data,
                sample=Sample(**sample.dict()),
                batch=batch,
                status_colors=STATUS_COLORS,
                page_id="sample_tris",
            )
        ),
    )
