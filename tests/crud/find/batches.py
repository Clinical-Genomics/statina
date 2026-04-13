from mongomock import MongoClient
from statina.adapter.plugin import StatinaAdapter
from statina.crud.find.batches import get_batch_ids_by_dataset


def test_get_batch_ids_by_dataset(database):
    # GIVEN a database with two batches belonging to "dataset_1" and one to "dataset_2"
    adapter = StatinaAdapter(database.client, db_name="testdb")
    adapter.batch_collection.insert_many([
        {"batch_id": "batch_1", "dataset": "dataset_1"},
        {"batch_id": "batch_2", "dataset": "dataset_1"},
        {"batch_id": "batch_3", "dataset": "dataset_2"},
    ])

    # WHEN fetching batch_ids for "dataset_1"
    batch_ids = get_batch_ids_by_dataset(adapter=adapter, dataset_name="dataset_1")

    # THEN only the two batch_ids belonging to "dataset_1" should be returned
    assert batch_ids == ["batch_1", "batch_2"]
