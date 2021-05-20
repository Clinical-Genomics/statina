from NIPTool.adapter import NiptAdapter
from NIPTool.crud.find import find


def get_last_batches(adapter: NiptAdapter, nr: int) -> list:
    """geting the <nr> last batches based on SequencingDate"""

    batch_sort_aggregation = [{"$sort": {"SequencingDate": -1}}]
    sorted_batches = list(find.batch_aggregate(pipe=batch_sort_aggregation, adapter=adapter))
    if len(sorted_batches) > nr:
        sorted_batches = sorted_batches[0:nr]

    return sorted_batches


def get_statistics_for_scatter_plot(batches: list, fields: list) -> dict:
    """Formating data for scatter plot"""

    scatter_plot_data = {}
    for batch in batches:
        batch_id = batch.get("batch_id")
        scatter_plot_data[batch_id] = {"date": batch.get("SequencingDate")}

        for field in fields:
            scatter_plot_data[batch_id][field] = batch.get(field)

    return scatter_plot_data


def get_statistics_for_box_plot(adapter: NiptAdapter, batches: list, fields: list):
    """Getting and formating data for box plot"""

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
    group = {"$group": {"_id": {"batch": "$batch_id", "date": "$batch.SequencingDate"}}}

    for field in fields:
        group["$group"][field] = {"$push": f"${field}"}

    pipe = [match, lookup, unwind, group]
    # maybe add a fina sort to the pipe
    box_plot_data = list(find.sample_aggregate(pipe=pipe, adapter=adapter))

    return box_plot_data
