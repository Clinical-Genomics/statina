
from NIPTool.server import create_app
from NIPTool.server.utils import get_last_batches
from NIPTool.adapter.plugin import NiptAdapter
from datetime import datetime


app = create_app(test= True)


def test_get_last_batches(database):
    app.db = database
    app.adapter = NiptAdapter(database.client, db_name = database.name)

    # GIVEN a database with four batch documents:
    batch1 = {"_id":"201860", "SequencingDate":"2022-03-10"}
    batch2 = {"_id":"201862", "SequencingDate":"2022-02-10"}
    batch3 = {"_id":"201830", "SequencingDate":"2022-02-09"}
    batch4 = {"_id":"101830", "SequencingDate":"2021-03-10"}

    database.batch.insert_many([batch4, batch1, batch3, batch2])
 
    # WHEN running get_last_batches with nr=2
    results = get_last_batches(adapter=app.adapter, nr=2)

    # THEN the results should contain the two batches with the latest SequencingDate
    assert results == [batch1, batch2]