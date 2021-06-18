from typing import Dict, List

from fastapi import APIRouter, Depends, Request

import statina.crud.find.plots.fetal_fraction_plot_data as get_fetal_fraction
from statina.adapter import StatinaAdapter
from statina.API.external.api.deps import get_current_user
from statina.API.external.constants import TRISOMI_TRESHOLDS
from statina.config import get_nipt_adapter, templates
from statina.crud.find import find
from statina.crud.find.plots.coverage_plot_data import (
    get_box_data_for_coverage_plot,
    get_scatter_data_for_coverage_plot,
)
from statina.crud.find.plots.zscore_plot_data import (
    get_samples_for_samp_tris_plot,
    get_tris_control_abnormal,
    get_tris_control_normal,
    get_tris_samples,
    get_normal_for_samp_tris_plot,
    get_abnormal_for_samp_tris_plot,
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


@router.post("/")
def batches(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """List of all batches"""

    all_batches: List[Batch] = find.batches(adapter=adapter)
    return templates.TemplateResponse(
        "batches.html",
        context={
            "request": request,
            "batches": all_batches,
            "current_user": user,
            "page_id": "all_batches",
        },
    )


@router.get("/")
def batches(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """List of all batches"""
    all_batches: List[Batch] = find.batches(adapter=adapter)
    return templates.TemplateResponse(
        "batches.html",
        context={
            "request": request,
            "batches": all_batches,
            "current_user": user,
            "page_id": "all_batches",
        },
    )


@router.post("/{batch_id}/")
def batch(
    request: Request,
    batch_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Batch view with table of all samples in the batch."""

    samples: List[DataBaseSample] = find.batch_samples(batch_id=batch_id, adapter=adapter)
    return templates.TemplateResponse(
        "batch/tabs/table.html",
        context={
            "request": request,
            "batch": find.batch(batch_id=batch_id, adapter=adapter),
            "sample_info": [Sample(**sample.dict()) for sample in samples],
            "page_id": "batches",
            "current_user": user,
        },
    )


@router.get("/{batch_id}/")
def batch(
    request: Request,
    batch_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Batch view with table of all samples in the batch."""

    samples: List[DataBaseSample] = find.batch_samples(batch_id=batch_id, adapter=adapter)
    return templates.TemplateResponse(
        "batch/tabs/table.html",
        context={
            "request": request,
            "batch": find.batch(batch_id=batch_id, adapter=adapter),
            "sample_info": [Sample(**sample.dict()) for sample in samples],
            "page_id": "batches",
            "current_user": user,
        },
    )


@router.get("/{batch_id}/{ncv}")
def Zscore(
    request: Request,
    batch_id: str,
    ncv: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Batch view with with Zscore plot"""

    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)

    return templates.TemplateResponse(
        "batch/tabs/Zscore.html",
        context=dict(
            request=request,
            tris_thresholds=TRISOMI_TRESHOLDS,
            batch=batch.dict(),
            chromosomes=[ncv],
            ncv_chrom_data={ncv: get_tris_samples(adapter=adapter, chr=ncv, batch_id=batch_id)},
            normal_data={ncv: get_tris_control_normal(adapter, ncv)},
            abnormal_data={ncv: get_tris_control_abnormal(adapter, ncv, 0)},
            page_id=f"batches_NCV{ncv}",
            current_user=user,
        ),
    )


@router.get("/batches/{batch_id}/fetal_fraction_XY")
def fetal_fraction_XY(
    request: Request,
    batch_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Batch view with fetal fraction (X against Y) plot"""

    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)

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

    x_max = max(control.FFX) + 1
    x_min = min(control.FFX) - 1

    sex_thresholds = SexChromosomeThresholds(x_min=x_min, x_max=x_max)
    return templates.TemplateResponse(
        "batch/tabs/FF_XY.html",
        context=dict(
            sex_thresholds={
                "XY_horisontal": sex_thresholds.XY_horizontal(),
                "XX_lower": sex_thresholds.XX_lower(),
                "XX_upper": sex_thresholds.XX_upper(),
                "XY_lower": sex_thresholds.XY_lower(),
                "XY_upper": sex_thresholds.XY_upper(),
                "XXY": sex_thresholds.XXY(),
            },
            request=request,
            current_user=user,
            control=control,
            abnormal=abnormal_dict,
            cases=get_fetal_fraction.samples(adapter=adapter, batch_id=batch_id),
            max_x=x_max,
            min_x=x_min,
            batch=batch.dict(),
            page_id="batches_FF_XY",
        ),
    )


@router.get("/batches/{batch_id}/fetal_fraction")
def fetal_fraction(
    request: Request,
    batch_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Batch view with fetal fraction plot"""
    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)
    return templates.TemplateResponse(
        "batch/tabs/FF.html",
        context=dict(
            request=request,
            current_user=user,
            control=get_fetal_fraction.samples(
                adapter=adapter, batch_id=batch_id, control_samples=True
            ),
            cases=get_fetal_fraction.samples(adapter=adapter, batch_id=batch_id),
            batch=batch.dict(),
            page_id="batches_FF",
        ),
    )


@router.get("/batches/{batch_id}/coverage")
def coverage(
    request: Request,
    batch_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Batch view with coverage plot"""
    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)
    db_samples: List[DataBaseSample] = find.batch_samples(batch_id=batch_id, adapter=adapter)
    samples: List[Sample] = [Sample(**db_sample.dict()) for db_sample in db_samples]

    scatter_data: Dict[str, CoveragePlotSampleData] = get_scatter_data_for_coverage_plot(samples)
    box_data: Dict[int, List[float]] = get_box_data_for_coverage_plot(samples)
    return templates.TemplateResponse(
        "batch/tabs/coverage.html",
        context=dict(
            request=request,
            current_user=user,
            batch=batch.dict(),
            x_axis=list(range(1, 23)),
            scatter_data=scatter_data,
            box_data=box_data,
            page_id="batches_cov",
        ),
    )


@router.get("/batches/{batch_id}/report/{coverage}")
def report(
    request: Request,
    batch_id: str,
    coverage: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Report view, collecting all tables and plots from one batch."""

    db_samples: List[DataBaseSample] = find.batch_samples(batch_id=batch_id, adapter=adapter)
    samples: List[Sample] = [Sample(**db_sample.dict()) for db_sample in db_samples]
    scatter_data: Dict[str, CoveragePlotSampleData] = get_scatter_data_for_coverage_plot(samples)
    box_data: Dict[int, List[float]] = get_box_data_for_coverage_plot(samples)
    control: FetalFractionSamples = get_fetal_fraction.samples(
        adapter=adapter, batch_id=batch_id, control_samples=True
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

    return templates.TemplateResponse(
        "batch/report.html",
        context=dict(
            # common
            request=request,
            current_user=user,
            batch=find.batch(batch_id=batch_id, adapter=adapter),
            # Zscore
            tris_thresholds=TRISOMI_TRESHOLDS,
            chromosomes=["13", "18", "21"],
            ncv_chrom_data=get_samples_for_samp_tris_plot(adapter, batch_id=batch_id).dict(
                by_alias=True
            ),
            normal_data=get_normal_for_samp_tris_plot(adapter).dict(by_alias=True),
            abnormal_data=get_abnormal_for_samp_tris_plot(adapter),
            # Fetal Fraction preface
            control=control,
            cases=get_fetal_fraction.samples(adapter=adapter, batch_id=batch_id),
            # Fetal Fraction  XY
            abnormal=abnormal_dict,
            max_x=max(control.FFX) + 1,
            min_x=min(control.FFX) - 1,
            # table
            sample_info=samples,
            # coverage
            coverage=coverage,
            x_axis=list(range(1, 23)),
            scatter_data=scatter_data,
            box_data=box_data,
            page_id="batches",
        ),
    )
