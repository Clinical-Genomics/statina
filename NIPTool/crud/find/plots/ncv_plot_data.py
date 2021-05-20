from NIPTool.models.server.plots.ncv import NCVSamples
from NIPTool.API.external.constants import STATUS_CLASSES
from NIPTool.adapter import NiptAdapter
from NIPTool.crud.find import find
from NIPTool.models.database import DataBaseSample


def get_tris_control_normal(adapter: NiptAdapter, chr) -> NCVSamples:
    """Normal Control Samples for trisomi plots"""

    pipe = [
        {"$match": {f"status_{chr}": {"$eq": "Normal"}, "include": {"$eq": True}}},
        {
            "$group": {
                "_id": {f"status_{chr}": f"$status_{chr}"},
                "values": {"$push": f"$Zscore_{chr}"},
                "names": {"$push": "$sample_id"},
                "count": {"$sum": 1},
            }
        },
    ]
    if not list(find.sample_aggregate(pipe=pipe, adapter=adapter)):
        return {}
    data = find.sample_aggregate(pipe=pipe, adapter=adapter)[0]

    return NCVSamples(**data)


def get_tris_control_abnormal(adapter: NiptAdapter, chr, x_axis):
    """Abnormal Control Samples for trisomi plots"""

    ##Continue here

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
                "values": {"$push": f"$Zscore_{chr}"},
                "names": {"$push": "$sample_id"},
                "count": {"$sum": 1},
            }
        },
    ]

    for status_dict in find.sample_aggregate(pipe=pipe, adapter=adapter):
        status = status_dict["_id"][f"status_{chr}"]
        plot_data[status] = {
            "values": [value for value in status_dict.get("values")],
            "names": status_dict.get("names"),
            "count": status_dict.get("count"),
            "x_axis": [x_axis] * status_dict.get("count"),
        }
    return plot_data


def get_tris_cases(adapter: NiptAdapter, chr, batch_id: str):
    """Cases for trisomi plots."""

    pipe = [
        {"$match": {"batch_id": {"$eq": batch_id}, "include": {"$eq": True}}},
        {
            "$group": {
                "_id": {"batch": "$batch_id"},
                "values": {"$push": f"$Zscore_{chr}"},
                "names": {"$push": "$sample_id"},
                "count": {"$sum": 1},
            }
        },
    ]

    if not list(find.sample_aggregate(pipe=pipe, adapter=adapter)):
        return {}

    data = list(find.sample_aggregate(pipe=pipe, adapter=adapter))[0]
    data["values"] = [value for value in data.get("values")]
    data["x_axis"] = list(range(1, data.get("count") + 1))
    return data


def get_abn_for_samp_tris_plot(adapter: NiptAdapter):
    """Format abnormal Control Samples for Sample trisomi plot"""

    plot_data = {}
    data_per_abnormaliy = {}
    for status in STATUS_CLASSES:
        plot_data[status] = {"values": [], "names": [], "count": 0, "x_axis": []}
    x_axis = 1
    for abn in ["13", "18", "21"]:
        data = get_tris_control_abnormal(adapter, abn, x_axis)
        data_per_abnormaliy[abn] = data

        for status, status_dict in data.items():
            plot_data[status]["values"] += status_dict.get("values", [])
            plot_data[status]["names"] += status_dict.get("names", [])
            plot_data[status]["count"] += status_dict.get("count", 0)
            plot_data[status]["x_axis"] += status_dict.get("x_axis", [])
        x_axis += 1

    return plot_data, data_per_abnormaliy


def get_normal_for_samp_tris_plot(adapter: NiptAdapter):
    """Format normal Control Samples for Sample trisomi plot"""

    return {
        "13": get_tris_control_normal(adapter, "13"),
        "18": get_tris_control_normal(adapter, "18"),
        "21": get_tris_control_normal(adapter, "21"),
    }


def get_sample_for_samp_tris_plot(sample: DataBaseSample):
    """Case data for Sample trisomi plot"""

    return {
        "13": {"value": sample.Zscore_13, "x_axis": 1},
        "18": {"value": sample.Zscore_18, "x_axis": 2},
        "21": {"value": sample.Zscore_21, "x_axis": 3},
    }
