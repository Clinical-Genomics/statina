from typing import Optional

import statina
from statina.adapter import StatinaAdapter
from statina.API.external.constants import CHROM_ABNORM, SEX_CHROM_ABNORM
from statina.models.server.plots.fetal_fraction import (
    AbNormalityClasses,
    FetalFractionControlAbNormal,
    FetalFractionSamples,
)


def samples(
    adapter: StatinaAdapter, batch_id: str, control_samples: Optional[bool] = False
) -> FetalFractionSamples:
    """Samples for fetal fraction plot"""

    batch: dict = adapter.batch_collection.find_one({"batch_id": batch_id})
    dataset = batch.get("dataset")
    batches_exclude_list = [
        batch_id,
        *(
            batch.get("batch_id")
            for batch in list(
                adapter.batch_collection.find(
                    {"dataset": {"$ne": dataset}}, {"batch_id": 1, "_id": 0}
                )
            )
        ),
    ]

    match = {
        "$match": {
            "FF_Formatted": {"$ne": "None", "$exists": True},
            "FFY": {"$ne": "None", "$exists": True},
            "FFX": {"$ne": "None", "$exists": True},
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
        match["$match"]["batch_id"] = {"$nin": batches_exclude_list}
        match["$match"]["include"] = {"$eq": True}
        for abn in SEX_CHROM_ABNORM:
            match["$match"][f"status_{abn}"] = {"$eq": "Normal"}
    else:
        match["$match"]["batch_id"] = {"$eq": batch_id}

    relevant_aggregation_data = list(
        statina.crud.find.samples.sample_aggregate(pipe=[match, group], adapter=adapter)
    )
    if relevant_aggregation_data:
        return FetalFractionSamples(**relevant_aggregation_data[0])
    return FetalFractionSamples(FFY=[], FFX=[], FF=[], names=[], count=0)


def control_abnormal(adapter: StatinaAdapter) -> FetalFractionControlAbNormal:
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
        for status_dict in statina.crud.find.samples.sample_aggregate(pipe=pipe, adapter=adapter):
            status: str = status_dict["_id"][f"status_{abn}"]
            statuses[status] = status_dict

        plot_data[abn] = AbNormalityClasses(status_data_=statuses)
    return FetalFractionControlAbNormal(**plot_data)
