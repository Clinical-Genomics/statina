from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Request, Security, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from statina.API.v2.endpoints.login import get_current_active_user
from statina.adapter import StatinaAdapter
from statina.config import get_nipt_adapter
from statina.crud.find import find
from statina.crud.find.plots.zscore_plot_data import (
    get_abn_for_samp_tris_plot,
    get_normal_for_samp_tris_plot,
    get_sample_for_samp_tris_plot,
)
from statina.models.database import Batch, DataBaseSample, User
from statina.models.server.plots.ncv import Zscore131821, ZscoreSamples

router = APIRouter(prefix="/v2")


@router.get("/samples/")
def samples(
    page_size: Optional[int] = Query(5),
    page_num: Optional[int] = Query(0),
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Get sample with id"""
    samples: List[DataBaseSample] = find.samples(
        adapter=adapter, page_size=page_size, page_num=page_num
    )
    return JSONResponse(content=jsonable_encoder(samples))


@router.get("/sample/{sample_id}")
def sample(
    sample_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Get sample with id"""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)

    return JSONResponse(sample.json())


@router.get("/samples/{sample_id}/tris")
def sample_tris(
    sample_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
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
                normal_data=normal_data.dict(exclude_none=True, by_alias=True),
                abnormal_data=abnormal_data,
                sample_data=sample_data,
            )
        ),
    )
