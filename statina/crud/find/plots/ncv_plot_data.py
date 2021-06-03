from copy import deepcopy
from typing import Dict, Optional

from statina.adapter import StatinaAdapter
from statina.crud.find import find
from statina.models.database import DataBaseSample
from statina.models.server.plots.ncv import NCV131821, NCVSamples


def get_tris_control_abnormal(adapter: StatinaAdapter, chr, x_axis) -> Dict[str, NCVSamples]:
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
                "ncv_values": {"$push": f"$Zscore_{chr}"},
                "names": {"$push": "$sample_id"},
                "count": {"$sum": 1},
            }
        },
    ]

    for status_dict in find.sample_aggregate(pipe=pipe, adapter=adapter):
        status = status_dict["_id"][f"status_{chr}"]
        plot_data[status] = NCVSamples(
            ncv_values=[value for value in status_dict.get("ncv_values")],
            names=status_dict.get("names"),
            count=status_dict.get("count"),
            x_axis=[x_axis] * status_dict.get("count"),
        )

    return plot_data


def get_abn_for_samp_tris_plot(adapter: StatinaAdapter) -> Dict[str, NCVSamples]:
    """Format abnormal Control Samples for Sample trisomi plot"""

    plot_data = {}

    for x_axis, abn in enumerate(["13", "18", "21"], start=1):
        tris_control_abnormal: Dict[str, NCVSamples] = get_tris_control_abnormal(
            adapter, abn, x_axis
        )
        for status, data in tris_control_abnormal.items():
            if status not in plot_data:
                plot_data[status] = deepcopy(data)
                continue
            plot_data[status] = NCVSamples(
                ncv_values=plot_data[status].ncv_values + data.ncv_values,
                names=plot_data[status].names + data.names,
                count=plot_data[status].count + data.count,
                x_axis=plot_data[status].x_axis + data.x_axis,
            )
    return plot_data


def get_tris_control_normal(
    adapter: StatinaAdapter, chr: str, x_axis: Optional[int] = None
) -> NCVSamples:
    """Normal Control Samples for trisomi plots"""

    pipe = [
        {"$match": {f"status_{chr}": {"$eq": "Normal"}, "include": {"$eq": True}}},
        {
            "$group": {
                "_id": {f"status_{chr}": f"$status_{chr}"},
                "ncv_values": {"$push": f"$Zscore_{chr}"},
                "names": {"$push": "$sample_id"},
                "count": {"$sum": 1},
            }
        },
    ]
    if not list(find.sample_aggregate(pipe=pipe, adapter=adapter)):
        return {}
    data = find.sample_aggregate(pipe=pipe, adapter=adapter)[0]
    if x_axis:
        data["x_axis"] = [x_axis] * data.get("count")

    return NCVSamples(**data)


def get_normal_for_samp_tris_plot(adapter: StatinaAdapter) -> NCV131821:
    """Format normal Control Samples for Sample trisomi plot"""

    return NCV131821(
        ncv_13=get_tris_control_normal(adapter=adapter, chr="13", x_axis=1),
        ncv_18=get_tris_control_normal(adapter=adapter, chr="18", x_axis=2),
        ncv_21=get_tris_control_normal(adapter=adapter, chr="21", x_axis=3),
    )


def get_samples_for_report_ncv_plot(adapter: StatinaAdapter, batch_id: str) -> NCV131821:
    return NCV131821(
        ncv_13=get_tris_samples(adapter=adapter, chr="13", batch_id=batch_id),
        ncv_18=get_tris_samples(adapter=adapter, chr="18", batch_id=batch_id),
        ncv_21=get_tris_samples(adapter=adapter, chr="21", batch_id=batch_id),
    )


def get_tris_samples(adapter: StatinaAdapter, chr, batch_id: str) -> NCVSamples:
    """Cases for trisomi plots."""

    pipe = [
        {"$match": {"batch_id": {"$eq": batch_id}, "include": {"$eq": True}}},
        {
            "$group": {
                "_id": {"batch": "$batch_id"},
                "ncv_values": {"$push": f"$Zscore_{chr}"},
                "names": {"$push": "$sample_id"},
                "count": {"$sum": 1},
            }
        },
    ]

    if not list(find.sample_aggregate(pipe=pipe, adapter=adapter)):
        return {}

    data = list(find.sample_aggregate(pipe=pipe, adapter=adapter))[0]
    data["x_axis"] = list(range(1, data.get("count") + 1))

    return NCVSamples(**data)


def get_sample_for_samp_tris_plot(sample: DataBaseSample) -> NCVSamples:
    """Case data for Sample trisomi plot"""
    return NCVSamples(
        ncv_values=[sample.Zscore_13, sample.Zscore_18, sample.Zscore_21],
        names=[sample.sample_id, sample.sample_id, sample.sample_id],
        x_axis=[1, 2, 3],
    )
