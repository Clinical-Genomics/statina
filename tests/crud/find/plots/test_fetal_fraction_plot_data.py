from statina.adapter.plugin import StatinaAdapter
from statina.crud.find.plots.fetal_fraction_plot_data import control_abnormal, samples


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

def make_abnormal_sample(sample_id, batch_id, status_X0="Normal", FFX=10.0, FFY=0.0):
    return {
        "sample_id": sample_id,
        "batch_id": batch_id,
        "FFX": FFX,
        "FFY": FFY,
        "include": True,
        "status_X0": status_X0,
        "status_XXX": "Normal",
        "status_XXY": "Normal",
        "status_XYY": "Normal",
        "status_13": "Normal",
        "status_18": "Normal",
        "status_21": "Normal",
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


def test_control_abnormal_returns_samples_grouped_by_status(database):
    # GIVEN a dataset with one batch and two abnormal X0 samples with different classifications
    nipt_adapter = StatinaAdapter(database.client, db_name="testdb")
    nipt_adapter.batch_collection.insert_one({"batch_id": "batch_A", "dataset": "dataset_A"})
    nipt_adapter.sample_collection.insert_many(
        [
            make_abnormal_sample("verified_sample", "batch_A", status_X0="Verified", FFX=9.0),
            make_abnormal_sample("probable_sample", "batch_A", status_X0="Probable", FFX=8.0),
        ]
    )

    # WHEN fetching control abnormal data for the dataset
    result = control_abnormal(adapter=nipt_adapter, dataset_name="dataset_A")

    # THEN the X0 group should contain both samples split by their classification
    assert result.X0.verified is not None
    assert "verified_sample" in result.X0.verified.names
    assert result.X0.probable is not None
    assert "probable_sample" in result.X0.probable.names


def test_control_abnormal_returns_empty_classes_when_no_batches_in_dataset(database):
    # GIVEN a database with no batches belonging to the requested dataset
    nipt_adapter = StatinaAdapter(database.client, db_name="testdb")

    # WHEN fetching control abnormal data for a dataset that does not exist
    result = control_abnormal(adapter=nipt_adapter, dataset_name="nonexistent_dataset")

    # THEN all abnormality classes should be empty (no samples matched)
    assert result.X0.verified is None
    assert result.X0.probable is None
    assert result.XXX.verified is None
    assert result.XXY.verified is None
    assert result.XYY.verified is None
