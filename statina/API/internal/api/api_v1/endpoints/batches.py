from typing import Dict, List

from fastapi import APIRouter, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import statina.crud.find.plots.fetal_fraction_plot_data as get_fetal_fraction
from statina.adapter import StatinaAdapter
from statina.API.external.api.deps import get_current_user
from statina.API.external.constants import TRISOMI_TRESHOLDS, COLORS
from statina.config import get_nipt_adapter, templates
from statina.crud.find import find
from statina.crud.find.plots.coverage_plot_data import (
    get_box_data_for_coverage_plot,
    get_scatter_data_for_coverage_plot,
)
from statina.crud.find.plots.zscore_plot_data import (
    get_tris_control_abnormal,
    get_tris_control_normal,
    get_tris_samples,
)
from statina.models.database import Batch, DataBaseSample, User
from statina.models.server.plots.coverage import CoveragePlotSampleData
from statina.models.server.plots.fetal_fraction import (
    FetalFractionControlAbNormal,
    FetalFractionSamples,
)
from statina.models.server.plots.fetal_fraction_sex import SexChromosomeThresholds
from statina.models.server.sample import Sample

router = APIRouter()

user = {}


@router.post("/")
def batches(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """List of all batches"""

    all_batches: List[Batch] = find.batches(adapter=adapter)
    return JSONResponse(
        content={
            "batches": jsonable_encoder(all_batches),
            "current_user": user,
            "page_id": "all_batches",
        },
    )


@router.get("/")
def batches(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """List of all batches"""
    all_batches: List[Batch] = find.batches(adapter=adapter)
    return JSONResponse(
        content=jsonable_encoder(
            {
                "batches": all_batches,
                "current_user": user,
                "page_id": "all_batches",
            }
        ),
    )


@router.post("/{batch_id}/")
def batch(
    request: Request,
    batch_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with table of all samples in the batch."""

    samples: List[DataBaseSample] = find.batch_samples(batch_id=batch_id, adapter=adapter)
    return JSONResponse(
        content=jsonable_encoder(
            {
                "batch": find.batch(batch_id=batch_id, adapter=adapter),
                "sample_info": [Sample(**sample.dict()) for sample in samples],
                "page_id": "batches",
                "current_user": user,
            }
        ),
    )


@router.get("/{batch_id}/")
def batch(
    request: Request,
    batch_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with table of all samples in the batch."""

    samples: List[DataBaseSample] = find.batch_samples(batch_id=batch_id, adapter=adapter)
    return JSONResponse(
        content=jsonable_encoder(
            {
                "batch": find.batch(batch_id=batch_id, adapter=adapter),
                "sample_info": [Sample(**sample.dict()) for sample in samples],
                "page_id": "batches",
                "current_user": user,
            }
        ),
    )


@router.get("/{batch_id}/{ncv}")
def Zscore(
    request: Request,
    batch_id: str,
    ncv: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with with Zscore plot"""

    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)

    return JSONResponse(
        content=jsonable_encoder(
            dict(
                tris_thresholds=TRISOMI_TRESHOLDS,
                batch=batch.dict(),
                chromosomes=[ncv],
                ncv_chrom_data={ncv: get_tris_samples(adapter=adapter, chr=ncv, batch_id=batch_id)},
                normal_data={ncv: get_tris_control_normal(adapter, ncv)},
                abnormal_data={ncv: get_tris_control_abnormal(adapter, ncv, 0)},
                page_id=f"batches_NCV{ncv}",
                current_user=user,
            )
        ),
    )


@router.get("/batches/{batch_id}/fetal_fraction_XY")
def fetal_fraction_XY(
    request: Request,
    batch_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with fetal fraction (X against Y) plot"""

    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)

    cases = get_fetal_fraction.samples(adapter=adapter, batch_id=batch_id)
    control: FetalFractionSamples = get_fetal_fraction.samples(
        batch_id=batch_id, adapter=adapter, control_samples=True
    )
    abnormal: FetalFractionControlAbNormal = get_fetal_fraction.control_abnormal(adapter)
    abnormal_dict = abnormal.dict(
        exclude_none=True,
        exclude={
            "X0": {"status_data_"},
            "XXX": {"status_data_"},
            "XXY": {"status_data_"},
            "XYY": {"status_data_"},
        },
    )

    x_max = max(control.FFX + cases.FFX) + 1
    x_min = min(control.FFX + cases.FFX) - 1

    sex_thresholds = SexChromosomeThresholds(x_min=x_min, x_max=x_max)
    return JSONResponse(
        content=jsonable_encoder(
            dict(
                sex_thresholds={
                    "XY_fetal_fraction_y": sex_thresholds.XY_fetal_fraction_y(),
                    "XX_lower": sex_thresholds.XX_lower(),
                    "XX_upper": sex_thresholds.XX_upper(),
                    "XY_upper": sex_thresholds.XY_upper(),
                    "XY_lower": sex_thresholds.XY_lower(),
                    "XXY": sex_thresholds.XXY(),
                },
                current_user=user,
                colors=COLORS,
                control=control,
                abnormal=abnormal_dict,
                cases=cases,
                max_x=x_max,
                min_x=x_min,
                batch=batch.dict(),
                page_id="batches_FF_XY",
            )
        ),
    )


@router.get("/batches/{batch_id}/fetal_fraction")
def fetal_fraction(
    request: Request,
    batch_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with fetal fraction plot"""
    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)
    return JSONResponse(
        content=jsonable_encoder(
            dict(
                current_user=user,
                colors=COLORS,
                control=get_fetal_fraction.samples(
                    adapter=adapter, batch_id=batch_id, control_samples=True
                ),
                cases=get_fetal_fraction.samples(adapter=adapter, batch_id=batch_id),
                batch=batch.dict(),
                page_id="batches_FF",
            )
        ),
    )


@router.get("/batches/{batch_id}/coverage")
def coverage(
    request: Request,
    batch_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with coverage plot"""
    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)
    db_samples: List[DataBaseSample] = find.batch_samples(batch_id=batch_id, adapter=adapter)
    samples: List[Sample] = [Sample(**db_sample.dict()) for db_sample in db_samples]

    scatter_data: Dict[str, CoveragePlotSampleData] = get_scatter_data_for_coverage_plot(samples)
    box_data: Dict[int, List[float]] = get_box_data_for_coverage_plot(samples)
    return JSONResponse(
        content=jsonable_encoder(
            dict(
                current_user=user,
                batch=batch.dict(),
                x_axis=list(range(1, 23)),
                scatter_data=scatter_data,
                box_data=box_data,
                page_id="batches_cov",
            )
        ),
    )
