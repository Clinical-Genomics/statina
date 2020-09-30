from NIPTool.server import create_app
from NIPTool.server.utils import get_last_batches
from NIPTool.adapter.plugin import NiptAdapter
from datetime import datetime


app = create_app(test=True)


def test_get_last_batches(database):
    app.db = database
    app.adapter = NiptAdapter(database.client, db_name=database.name)

    # GIVEN a database with four batch documents:
    batch1 = {"SequencingDate": "2022-03-10"}
    batch2 = {"SequencingDate": "2022-02-10"}
    batch3 = {"SequencingDate": "2022-02-09"}
    batch4 = {"SequencingDate": "2021-03-10"}

    database.batch.insert_many([batch4, batch1, batch3, batch2])

    # WHEN running get_last_batches with nr=3
    results = get_last_batches(adapter=app.adapter, nr=3)

    # THEN the results should contain the thre batches with the latest
    # SequencingDate, sorted by SequencingDate
    assert results == [batch1, batch2, batch3]


def test_get_last_batches_to_fiew_batches_in_database(database):
    app.db = database
    app.adapter = NiptAdapter(database.client, db_name=database.name)

    # GIVEN a database with four batch documents:
    batch1 = {"SequencingDate": "2022-03-10"}
    batch2 = {"SequencingDate": "2022-02-10"}
    batch3 = {"SequencingDate": "2022-02-09"}
    batch4 = {"SequencingDate": "2021-03-10"}

    database.batch.insert_many([batch4, batch1, batch3, batch2])

    # WHEN running get_last_batches with nr=5
    results = get_last_batches(adapter=app.adapter, nr=5)

    # THEN the results should contain the four batches in the
    # database sorted by SequencingDate
    assert results == [batch1, batch2, batch3, batch4]


def test_get_statistics_for_box_plot(database, sample, batch):
    app.db = database
    app.adapter = NiptAdapter(database.client, db_name=database.name)
   
    # GIVEN a database with
    database.batch.insert_many(
        [batch(batch_id="201860"), batch(batch_id="201861"), batch(batch_id="201862")]
    )
    database.sample.insert_many(
        [
            sample(batch_id="201860", ratio_13=0.97, fetal_fraction=11.5),
            sample(batch_id="201860", ratio_13=0.97, fetal_fraction=11.5),
            sample(batch_id="201860", ratio_13=0.97, fetal_fraction=11.5),
            sample(batch_id="201861", ratio_13=0.97, fetal_fraction=11.5),
            sample(batch_id="201861", ratio_13=0.97, fetal_fraction=11.5),
            sample(batch_id="201861", ratio_13=0.97, fetal_fraction=11.5),
            sample(batch_id="201862", ratio_13=0.97, fetal_fraction=11.5),
            sample(batch_id="201862", ratio_13=0.97, fetal_fraction=11.5),
            sample(batch_id="201862", ratio_13=0.97, fetal_fraction=11.5),
        ]
    )

    # WHEN running get_statistics_for_box_plot
    results = get_statistics_for_box_plot(
        adapter=app.adapter,
        batches=["201860", "201861", "201862"],
        fields=["Ratio_13", "FF_Formatted"],
    )

    # THEN the results
    assert results == []