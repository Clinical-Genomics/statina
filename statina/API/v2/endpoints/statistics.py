from fastapi import APIRouter, Depends, Security
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from statina.adapter.plugin import StatinaAdapter
from statina.API.v2.endpoints.user import get_current_active_user
from statina.config import get_nipt_adapter
from statina.crud.find.plots.statistics_plot_data import (
    get_last_batches,
    get_statistics_for_box_plot,
    get_statistics_for_scatter_plot,
)
from statina.models.database import User

router = APIRouter(prefix="/v2")


@router.get("/statistics")
def statistics(
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
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
    return JSONResponse(
        content=jsonable_encoder(
            dict(
                ticks=list(range(nr_batches)),
                nr_batches=nr_batches,
                batch_ids=batch_ids,
                box_stat=box_stat,
                box_plots=box_plots,
                scatter_stat=scatter_stat,
                scatter_plots=scatter_plots,
            ),
            by_alias=False,
        )
    )
