from statina.adapter.plugin import StatinaAdapter
from statina.crud.find.plots.fetal_fraction_plot_data import samples


def make_sample(sample_id, batch_id):
    return {
        "sample_id": sample_id,
        "batch_id": batch_id,
        "FF_Formatted": 0.1,
        "FFY": 0.1,
        "FFX": 0.1,
        "include": True,
        "status_X0": "Normal",
        "status_XXX": "Normal",
        "status_XXY": "Normal",
        "status_XYY": "Normal",
    }


def test_control_samples_filtered_by_dataset(database):
    # GIVEN three batches: two in dataset_A and one in dataset_B, each with one sample
    nipt_adapter = StatinaAdapter(database.client, db_name="testdb")
    nipt_adapter.batch_collection.insert_many(
        [
            {"batch_id": "batch_to_search_with", "dataset": "dataset_A"},
            {"batch_id": "batch_same_dataset", "dataset": "dataset_A"},
            {"batch_id": "batch_different_dataset", "dataset": "dataset_B"},
        ]
    )
    nipt_adapter.sample_collection.insert_many(
        [
            make_sample("control_in_search_batch", "batch_to_search_with"),
            make_sample("control_same_dataset", "batch_same_dataset"),
            make_sample("control_different_dataset", "batch_different_dataset"),
        ]
    )

    # WHEN fetching control samples for batch_to_search_with
    result = samples(adapter=nipt_adapter, batch_id="batch_to_search_with", control_samples=True)

    # THEN only control_same_dataset from the same dataset should be returned
    assert result.count == 1
    assert result.names == ["control_same_dataset"]
