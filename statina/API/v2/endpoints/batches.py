from pathlib import Path
from typing import Dict, List

from fastapi import APIRouter, Depends, Request, Security
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import statina.crud.find.plots.fetal_fraction_plot_data as get_fetal_fraction
from statina.API.v2.endpoints.login import get_current_active_user
from statina.adapter import StatinaAdapter
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
from statina.crud.insert import insert_batch, insert_samples
from statina.models.database import Batch, DataBaseSample, User
from statina.models.server.load import BatchRequestBody
from statina.models.server.plots.coverage import CoveragePlotSampleData
from statina.models.server.plots.fetal_fraction import (
    FetalFractionControlAbNormal,
    FetalFractionSamples,
)
from statina.models.server.plots.fetal_fraction_sex import SexChromosomeThresholds
from statina.models.server.sample import Sample
from statina.parse.batch import get_samples, get_batch

router = APIRouter()


@router.get("/")
def batches(
    current_user: User = Depends(get_current_active_user),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """List of all batches"""
    all_batches: List[Batch] = find.batches(adapter=adapter)
    return JSONResponse(
        content=jsonable_encoder(
            {
                "batches": all_batches,
                "current_user": current_user,
                "page_id": "all_batches",
            }
        ),
    )


@router.post("/batch/")
def batch(
    batch_files: BatchRequestBody,
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Function to load batch data into the database with rest"""
    nipt_results = Path(batch_files.result_file)
    if not nipt_results.exists():
        return JSONResponse(content="Results file missing", status_code=422)
    samples: List[DataBaseSample] = get_samples(nipt_results)
    batch: Batch = get_batch(nipt_results)
    if find.batch(adapter=adapter, batch_id=batch.batch_id):
        return JSONResponse(content="Batch already in database!", status_code=422)
    insert_batch(adapter=adapter, batch=batch, batch_files=batch_files)
    insert_samples(adapter=adapter, samples=samples, segmental_calls=batch_files.segmental_calls)
    return JSONResponse(content=f"Batch {batch.batch_id} inserted to the database", status_code=200)


@router.get("/batch/{batch_id}")
def batch(
    batch_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with table of all samples in the batch."""

    return JSONResponse(find.batch(batch_id=batch_id, adapter=adapter), status_code=200)


@router.get("/batch/{batch_id}/samples")
def batch_samples(
    batch_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with table of all samples in the batch."""

    return JSONResponse(find.batch_samples(batch_id=batch_id, adapter=adapter), status_code=200)


@router.get("/{batch_id}/{ncv}")
def Zscore(
    batch_id: str,
    ncv: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with with Zscore plot"""

    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)

    return JSONResponse(
        content=jsonable_encoder(
            dict(
                tris_thresholds=TRISOMI_TRESHOLDS,
                chromosomes=[ncv],
                ncv_chrom_data={ncv: get_tris_samples(adapter=adapter, chr=ncv, batch_id=batch_id)},
                normal_data={ncv: get_tris_control_normal(adapter, ncv)},
                abnormal_data={ncv: get_tris_control_abnormal(adapter, ncv, 0)},
            )
        ),
    )


@router.get("/batches/{batch_id}/fetal_fraction_XY")
def fetal_fraction_XY(
    batch_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
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
                control=control,
                abnormal=abnormal_dict,
                cases=cases,
                max_x=x_max,
                min_x=x_min,
            )
        ),
    )


@router.get("/batches/{batch_id}/fetal_fraction")
def fetal_fraction(
    batch_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with fetal fraction plot"""
    return JSONResponse(
        content=jsonable_encoder(
            dict(
                control=get_fetal_fraction.samples(
                    adapter=adapter, batch_id=batch_id, control_samples=True
                ),
                cases=get_fetal_fraction.samples(adapter=adapter, batch_id=batch_id),
            )
        ),
    )


@router.get("/batches/{batch_id}/coverage")
def coverage(
    batch_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with coverage plot"""
    db_samples: List[DataBaseSample] = find.batch_samples(batch_id=batch_id, adapter=adapter)
    samples: List[Sample] = [Sample(**db_sample.dict()) for db_sample in db_samples]

    scatter_data: Dict[str, CoveragePlotSampleData] = get_scatter_data_for_coverage_plot(samples)
    box_data: Dict[int, List[float]] = get_box_data_for_coverage_plot(samples)
    return JSONResponse(
        content=jsonable_encoder(
            dict(
                x_axis=list(range(1, 23)),
                scatter_data=scatter_data,
                box_data=box_data,
            )
        ),
    )
