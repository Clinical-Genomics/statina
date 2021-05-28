from typing import Optional

from NIPTool.models.server.plots.fetal_fraction import (
    FetalFractionSamples,
    FetalFractionControlAbNormal,
    AbNormalityClasses,
)
from NIPTool.API.external.constants import CHROM_ABNORM, SEX_CHROM_ABNORM
from NIPTool.adapter import NiptAdapter
from NIPTool.crud.find import find


def samples(
    adapter: NiptAdapter, batch_id: Optional[str] = None, control_samples: Optional[bool] = False
) -> FetalFractionSamples:
    """Samples for fetal fraction plot"""

    match = {
        "$match": {
            "FF_Formatted": {"$ne": "None", "$exists": True},
            "FFY": {"$ne": "None", "$exists": True},
            "FFX": {"$ne": "None", "$exists": True},
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

    if control_samples:
        match["$match"]["batch_id"] = {"$ne": batch_id}
        for abn in SEX_CHROM_ABNORM:
            match["$match"][f"status_{abn}"] = {"$eq": "Normal"}
    else:
        match["$match"]["batch_id"] = {"$eq": batch_id}

    relevant_aggregation_data = list(find.sample_aggregate(pipe=[match, group], adapter=adapter))[0]
    return FetalFractionSamples(**relevant_aggregation_data)


def control_abnormal(adapter: NiptAdapter) -> FetalFractionControlAbNormal:
    """Abnormal Control Samples for fetal_fraction_XY plot"""

    plot_data = {}
    for abn in CHROM_ABNORM:
        plot_data[abn] = {}
        pipe = [
            {
                "$match": {
                    f"status_{abn}": {"$ne": "Normal", "$exists": True},
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
        statuses = {}
        for status_dict in find.sample_aggregate(pipe=pipe, adapter=adapter):
            status: str = status_dict["_id"][f"status_{abn}"]
            statuses[status] = status_dict

        plot_data[abn] = AbNormalityClasses(status_data_=statuses)
    return FetalFractionControlAbNormal(**plot_data)