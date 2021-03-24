from NIPTool.load.batch import load_batch
from NIPTool.parse.batch import get_samples, get_batch

from NIPTool.load.user import load_user
from NIPTool.adapter.plugin import NiptAdapter


def test_load_user(database, valid_load_user):
    # GIVEN a user with valid requiered fields and a nipt database adapter
    nipt_adapter = NiptAdapter(database.client, db_name='test')

    # WHEN running load_user
    load_user(nipt_adapter, valid_load_user)

    # The user should be added to the database
    assert nipt_adapter.user_collection.estimated_document_count() == 1


def test_batch_valid_files(database, valid_csv, valid_load_batch):
    # GIVEN the following request data:
    #   a valid csv file with three samples
    #   segmental_calls and multiqc_report files with random content, but that do exist.
    nipt_adapter = NiptAdapter(database.client, db_name='test')
    batch = get_batch(valid_csv)

    # WHEN running load_batch
    load_batch(nipt_adapter, batch, valid_load_batch)

    # THEN the batch should be added to the batch collection
    assert nipt_adapter.batch_collection.estimated_document_count() == 1


"""def test_samples_valid_files(database, valid_csv, segmental_calls, multiqc_report):
    # GIVEN the following request data:
    #   a valid csv file with three samples
    #   segmental_calls and multiqc_report files with random content, but that do exist.

    data = dict(multiqc_report=multiqc_report, segmental_calls=segmental_calls, result_file=valid_csv)

    # WHEN running the request with the data
    response = fast_app_client.post('/batch', data=data)

    # THEN assert the samples should be added to the sample collection
    # and the batch should be added to the batch collection
    assert mock_app.adapter.sample_collection.estimated_document_count() == 3
    assert mock_app.adapter.batch_collection.estimated_document_count() == 1
    resp_data = json.loads(response.data)
    assert resp_data["message"] == "Data loaded into database"
    assert response.status_code == 200"""
