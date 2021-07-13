from fastapi import APIRouter, Depends, Request

from statina.adapter.plugin import StatinaAdapter
from statina.API.external.api.deps import get_current_user
from statina.config import get_nipt_adapter, templates
from statina.crud.find.plots.statistics_plot_data import (
    get_last_batches,
    get_statistics_for_box_plot,
    get_statistics_for_scatter_plot,
)
from statina.models.database import User

router = APIRouter()


@router.get("/statistics")
def statistics(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Statistics view."""

    nr_batches = 20
    scatter_plots = ["Stdev_13", "Stdev_18", "Stdev_21"]
    box_plots = [
        "Chr13_Ratio",
        "Chr18_Ratio",
        "Chr21_Ratio",
        "FF_Formatted",
        "DuplicationRate",
        "MappedReads",
        "GC_Dropout",
        "AT_Dropout",
        "Bin2BinVariance",
        "Library_nM",
    ]

    batches = get_last_batches(adapter=adapter, nr_of_batches=nr_batches)
    batch_ids = [batch.get("batch_id") for batch in batches]
    box_stat = get_statistics_for_box_plot(adapter=adapter, batches=batch_ids, fields=box_plots)
    scatter_stat = get_statistics_for_scatter_plot(batches=batches, fields=scatter_plots)
    return templates.TemplateResponse(
        "statistics.html",
        context=dict(
            request=request,
            current_user=user,
            ticks=list(range(0, nr_batches)),
            nr_batches=nr_batches,
            batch_ids=batch_ids,
            box_stat=box_stat,
            box_plots=box_plots,
            scatter_stat=scatter_stat,
            scatter_plots=scatter_plots,
            page_id="statistics",
        ),
    )
