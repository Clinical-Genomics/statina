from NIPTool.server import create_app
from NIPTool.server.utils import (
    get_last_batches,
    get_statistics_for_box_plot,
    get_statistics_for_scatter_plot,
)
from NIPTool.adapter.plugin import NiptAdapter
from conftest import batch, sample
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


def test_get_statistics_for_box_plot(database):
    app.db = database
    app.adapter = NiptAdapter(database.client, db_name=database.name)

    # GIVEN a database with thre batches and nine samples like below
    database.batch.insert_many(
        [batch(batch_id="201860"), batch(batch_id="201861"), batch(batch_id="201862")]
    )
    database.sample.insert_many(
        [
            sample(
                sample_id="07452-00",
                batch_id="201860",
                ratio_13=0.91,
                fetal_fraction=10.5,
            ),
            sample(
                sample_id="07452-01",
                batch_id="201860",
                ratio_13=0.92,
                fetal_fraction=11.5,
            ),
            sample(
                sample_id="07452-02",
                batch_id="201860",
                ratio_13=0.93,
                fetal_fraction=12.5,
            ),
            sample(
                sample_id="07452-03",
                batch_id="201861",
                ratio_13=0.94,
                fetal_fraction=13.5,
            ),
            sample(
                sample_id="07452-04",
                batch_id="201861",
                ratio_13=0.95,
                fetal_fraction=14.5,
            ),
            sample(
                sample_id="07452-05",
                batch_id="201861",
                ratio_13=0.96,
                fetal_fraction=15.5,
            ),
            sample(
                sample_id="07452-06",
                batch_id="201862",
                ratio_13=0.97,
                fetal_fraction=16.5,
            ),
            sample(
                sample_id="07452-07",
                batch_id="201862",
                ratio_13=0.98,
                fetal_fraction=17.5,
            ),
            sample(
                sample_id="07452-08",
                batch_id="201862",
                ratio_13=0.99,
                fetal_fraction=18.5,
            ),
        ]
    )

    # WHEN running get_statistics_for_box_plot
    results = get_statistics_for_box_plot(
        adapter=app.adapter,
        batches=["201860", "201861", "201862"],
        fields=["Ratio_13", "FF_Formatted"],
    )

    # THEN the results shoule be:
    expected_result = [
        {
            "FF_Formatted": [10.5, 11.5, 12.5],
            "Ratio_13": [0.91, 0.92, 0.93],
            "_id": {"batch": "201860", "date": "2022-03-10"},
        },
        {
            "FF_Formatted": [13.5, 14.5, 15.5],
            "Ratio_13": [0.94, 0.95, 0.96],
            "_id": {"batch": "201861", "date": "2022-03-10"},
        },
        {
            "FF_Formatted": [16.5, 17.5, 18.5],
            "Ratio_13": [0.97, 0.98, 0.99],
            "_id": {"batch": "201862", "date": "2022-03-10"},
        },
    ]
    assert results == expected_result


def test_get_statistics_for_scatter_plot(database):
    app.db = database
    app.adapter = NiptAdapter(database.client, db_name=database.name)

    # GIVEN a list with three batch documents:
    batches = [
        batch(batch_id="201860", stdev_13=0.02, stdev_21=0.01),
        batch(batch_id="201861", stdev_13=0.01, stdev_21=0.09),
        batch(batch_id="201862", stdev_13=0.05, stdev_21=0.08),
    ]

    # WHEN running get_statistics_for_scatter_plot
    results = get_statistics_for_scatter_plot(
        batches=batches, fields=["Stdev_13", "Stdev_21"]
    )

    # THEN the results should look like this:
    expected_result = {
        "201860": {"date": "2022-03-10", "Stdev_13": 0.02, "Stdev_21": 0.01},
        "201861": {"date": "2022-03-10", "Stdev_13": 0.01, "Stdev_21": 0.09},
        "201862": {"date": "2022-03-10", "Stdev_13": 0.05, "Stdev_21": 0.08},
    }
    assert results == expected_result
