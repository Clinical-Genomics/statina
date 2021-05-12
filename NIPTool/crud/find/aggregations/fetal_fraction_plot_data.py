from typing import List, Dict, Optional

from NIPTool.API.external.api.api_v1.models.plots.fetal_fraction import (
    FetalFraction,
    FetalFractionControlAbNormal,
    FetalFractionStatus,
)
from NIPTool.API.external.constants import CHROM_ABNORM
from NIPTool.adapter import NiptAdapter
from NIPTool.crud.find import find


def samples(adapter: NiptAdapter, batch_id: Optional[str] = None) -> FetalFraction:
    """Cases for fetal fraction plot"""

    match = {
        "$match": {
            "FF_Formatted": {"$ne": "None", "$exists": "True"},
            "FFY": {"$ne": "None", "$exists": "True"},
            "FFX": {"$ne": "None", "$exists": "True"},
            "include": {"$eq": True},
        }
    }
    group = {
        "$group": {
            "_id": "None",
            "FFY": {"$push": "$FFY"},
            "FFX": {"$push": "$FFX"},
            "FF": {"$push": "$FF_Formatted"},
            "names": {"$push": "$sample_id"},
            "count": {"$sum": 1},
        }
    }

    if batch_id:
        match["$match"]["batch_id"] = {"$eq": batch_id}

    # else:!!!!!!! Normal samples. Also exclude samples from batch?
    #    for abn in CHROM_ABNORM:
    #        match["$match"]["batch_id"] ={f"status_{abn}": {"$eq": "Normal", "$exists": "True"}

    relevant_aggregation_data = list(find.sample_aggregate(pipe=[match, group], adapter=adapter))[0]
    return FetalFraction(**relevant_aggregation_data)


def ff_control_abnormal_pipe(abn: str) -> List[Dict]:
    return [
        {
            "$match": {
                f"status_{abn}": {"$ne": "Normal", "$exists": "True"},
                "include": {"$eq": True},
            }
        },
        {
            "$group": {
                "_id": {f"status_{abn}": f"$status_{abn}"},
                "FFX": {"$push": "$FFX"},
                "FFY": {"$push": "$FFY"},
                "names": {"$push": "$sample_id"},
                "count": {"$sum": 1},
            }
        },
    ]


def control_abnormal(adapter: NiptAdapter) -> FetalFractionControlAbNormal:
    """Abnormal Control Samples for fetal_fraction_XY plot"""

    plot_data = {}
    for abn in CHROM_ABNORM:
        plot_data[abn] = {}
        pipe = ff_control_abnormal_pipe(abn)
        statuses = {}
        for status_dict in find.sample_aggregate(pipe=pipe, adapter=adapter):
            status: str = status_dict["_id"][f"status_{abn}"]
            statuses[status] = status_dict

        plot_data[abn] = FetalFractionStatus(status_data_=statuses)
    return FetalFractionControlAbNormal(**plot_data)
