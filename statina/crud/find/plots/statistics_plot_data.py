from typing import List, Optional

import pymongo

from statina.adapter import StatinaAdapter
from statina.crud.find import find


def get_last_batches(adapter, nr_of_batches: int) -> list:
    """getting the <nr_of_batches> last batches based on SequencingDate"""

    batches: pymongo.cursor = adapter.batch_collection.find().sort([("SequencingDate", -1)])
    return list(batches.limit(nr_of_batches))


def get_statistics_for_scatter_plot(batches: list, fields: list) -> dict:
    """Formatting data for scatter plot"""

    scatter_plot_data = {}
    for batch in batches:
        batch_id = batch.get("batch_id")
        scatter_plot_data[batch_id] = {"date": batch.get("SequencingDate")}

        for field in fields:
            scatter_plot_data[batch_id][field] = batch.get(field)

    return scatter_plot_data


def get_statistics_for_box_plot(adapter: StatinaAdapter, batches: list, fields: list):
    """Getting and formatting data for box plot"""

    match = {"$match": {"batch_id": {"$in": batches}}}
    lookup = {
        "$lookup": {
            "from": "batch",
            "localField": "batch_id",
            "foreignField": "batch_id",
            "as": "batch",
        }
    }
    unwind = {"$unwind": {"path": "$batch"}}
    group = {
        "$group": {
            "_id": {"batch": "$batch_id", "date": "$batch.SequencingDate"},
            "sample_ids": {"$push": "$sample_id"},
        },
    }

    for field in fields:
        group["$group"][field] = {"$push": f"${field}"}

    pipe = [match, lookup, unwind, group]
    # maybe add a fina sort to the pipe
    box_plot_data = list(find.sample_aggregate(pipe=pipe, adapter=adapter))
    return {batch["_id"]["batch"]: batch for batch in box_plot_data}
