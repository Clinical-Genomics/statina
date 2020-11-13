from NIPTool.commands.load.batch import batch
from NIPTool.server import create_app
from NIPTool.commands.base import cli
from NIPTool.adapter.plugin import NiptAdapter


app = create_app(test=True)


def test_batch_valid_file(database, valid_load_config):
    app.db = database
    app.adapter = NiptAdapter(database.client, db_name=database.name)

    # GIVEN a valid csv file with three samples

    # WHEN loading the batch file with correct foramted input string
    runner = app.test_cli_runner()
    runner.invoke(cli, ["load", "batch", "-b", valid_load_config])

    # THEN assert the samples should be added to the sample colleciton
    # and the batch should be added to the batch colleciton
    assert app.adapter.sample_collection.estimated_document_count() == 3
    assert app.adapter.batch_collection.estimated_document_count() == 1


def test_batch_invalid_file(database, invalid_load_config):
    app.db = database
    app.adapter = NiptAdapter(database.client, db_name=database.name)

    # GIVEN a invalid csv file

    # WHEN loading the batch file with correct foramted input string
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ["load", "batch", "-b", invalid_load_config])

    # THEN assert nothing added to sample or batch collections
    # THEN assert Badly formated csv! Can not load. Exiting.
    assert app.adapter.sample_collection.estimated_document_count() == 0
    assert app.adapter.batch_collection.estimated_document_count() == 0
    assert result.exit_code == 1


def test_batch_no_file(database):
    app.db = database
    app.adapter = NiptAdapter(database.client, db_name=database.name)

    # GIVEN a invalid csv file

    # WHEN loading the batch file with correct foramted input string
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ["load", "batch", "-b", "wrong/path"])

    # THEN assert nothing added to sample or batch collections
    # THEN assert Badly formated csv! Can not load. Exiting.
    assert app.adapter.sample_collection.estimated_document_count() == 0
    assert app.adapter.batch_collection.estimated_document_count() == 0
    assert result.exit_code == 1