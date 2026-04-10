from copy import deepcopy
from typing import Dict, Optional

import statina
from statina.adapter import StatinaAdapter
from statina.models.database import DataBaseSample
from statina.models.server.plots.ncv import Ratio131821, RatioSamples


def get_tris_control_abnormal(adapter: StatinaAdapter, chr, x_axis) -> Dict[str, RatioSamples]:
    """Abnormal Control Samples for trisomi plots"""

    plot_data = {}

    pipe = [
        {
            "$match": {
                f"status_{chr}": {"$ne": "Normal", "$exists": "True"},
                "include": {"$eq": True},
            }
        },
        {
            "$group": {
                "_id": {f"status_{chr}": f"$status_{chr}"},
                "ncv_values": {"$push": f"$Chr{chr}_Ratio"},
                "names": {"$push": "$sample_id"},
                "count": {"$sum": 1},
            }
        },
    ]

    for status_dict in statina.crud.find.samples.sample_aggregate(pipe=pipe, adapter=adapter):
        status = status_dict["_id"][f"status_{chr}"]
        plot_data[status] = RatioSamples(
            ncv_values=[value for value in status_dict.get("ncv_values")],
            names=status_dict.get("names"),
            count=status_dict.get("count"),
            x_axis=[x_axis] * status_dict.get("count"),
        )

    return plot_data


def get_abn_for_samp_tris_plot(adapter: StatinaAdapter) -> Dict[str, RatioSamples]:
    """Format abnormal Control Samples for Sample trisomi plot"""

    plot_data = {}

    for x_axis, abn in enumerate(["13", "18", "21"], start=1):
        tris_control_abnormal: Dict[str, RatioSamples] = get_tris_control_abnormal(
            adapter, abn, x_axis
        )
        for status, data in tris_control_abnormal.items():
            if status not in plot_data:
                plot_data[status] = deepcopy(data)
                continue
            plot_data[status] = RatioSamples(
                ncv_values=plot_data[status].ncv_values + data.ncv_values,
                names=plot_data[status].names + data.names,
                count=plot_data[status].count + data.count,
                x_axis=plot_data[status].x_axis + data.x_axis,
            )
    return plot_data


def get_tris_control_normal(
    adapter: StatinaAdapter, chr: str, dataset_name: str, x_axis: Optional[int] = None
) -> RatioSamples:
    """Normal Control Samples for trisomi plots"""

    pipe = [
        {"$match": {f"status_{chr}": {"$eq": "Normal"}, "include": {"$eq": True}}},
        {
            "$lookup": {
                "from": "batch",
                "localField": "batch_id",
                "foreignField": "batch_id",
                "as": "batch",
            }
        },
        {
            "$group": {
                "_id": {f"status_{chr}": f"$status_{chr}"},
                "ncv_values": {"$push": f"$Chr{chr}_Ratio"},
                "names": {"$push": "$sample_id"},
                "count": {"$sum": 1},
                "batch": {"$push": "$batch"},
            },
        },
        {
            "$unwind": {"path": "$batch"},
        },
        {"$match": {"batch.dataset": dataset_name}},
    ]
    if not list(statina.crud.find.samples.sample_aggregate(pipe=pipe, adapter=adapter)):
        return {}
    data = statina.crud.find.samples.sample_aggregate(pipe=pipe, adapter=adapter)[0]
    if x_axis:
        data["x_axis"] = [x_axis] * data.get("count")

    return RatioSamples(**data)


def get_normal_for_samp_tris_plot(adapter: StatinaAdapter, dataset_name: str) -> Ratio131821:
    """Format normal Control Samples for Sample trisomi plot"""

    return Ratio131821(
        chr_13=get_tris_control_normal(
            adapter=adapter, chr="13", dataset_name=dataset_name, x_axis=1
        ),
        chr_18=get_tris_control_normal(
            adapter=adapter, chr="18", dataset_name=dataset_name, x_axis=2
        ),
        chr_21=get_tris_control_normal(
            adapter=adapter, chr="21", dataset_name=dataset_name, x_axis=3
        ),
    )


def get_abnormal_for_samp_tris_plot(adapter: StatinaAdapter) -> dict:
    """Format normal Control Samples for Sample trisomi plot"""

    return {
        "13": get_tris_control_abnormal(adapter=adapter, chr="13", x_axis=0),
        "18": get_tris_control_abnormal(adapter=adapter, chr="18", x_axis=0),
        "21": get_tris_control_abnormal(adapter=adapter, chr="21", x_axis=0),
    }


def get_samples_for_samp_tris_plot(adapter: StatinaAdapter, batch_id: str) -> Ratio131821:
    return Ratio131821(
        chr_13=get_tris_samples(adapter=adapter, chr="13", batch_id=batch_id),
        chr_18=get_tris_samples(adapter=adapter, chr="18", batch_id=batch_id),
        chr_21=get_tris_samples(adapter=adapter, chr="21", batch_id=batch_id),
    )


def get_tris_samples(adapter: StatinaAdapter, chr, batch_id: str) -> RatioSamples:
    """Cases for trisomi plots."""

    pipe = [
        {"$match": {"batch_id": {"$eq": batch_id}}},
        {
            "$group": {
                "_id": {"batch": "$batch_id"},
                "ncv_values": {"$push": f"$Chr{chr}_Ratio"},
                "names": {"$push": "$sample_id"},
                "count": {"$sum": 1},
            }
        },
    ]

    if not list(statina.crud.find.samples.sample_aggregate(pipe=pipe, adapter=adapter)):
        return {}

    data = list(statina.crud.find.samples.sample_aggregate(pipe=pipe, adapter=adapter))[0]
    data["x_axis"] = list(range(1, data.get("count") + 1))

    return RatioSamples(**data)


def get_sample_for_samp_tris_plot(sample: DataBaseSample) -> RatioSamples:
    """Case data for Sample trisomi plot"""
    return RatioSamples(
        ncv_values=[sample.Chr13_Ratio, sample.Chr18_Ratio, sample.Chr21_Ratio],
        names=[sample.sample_id, sample.sample_id, sample.sample_id],
        x_axis=[1, 2, 3],
    )
