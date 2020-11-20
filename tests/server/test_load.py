
import pytest
from NIPTool.exeptions import NIPToolError, FileValidationError

def test_user(mock_app):
    #  GIVEN
    data = dict(email='maya.papaya@something.se', name="Maya Papaya", role="RW")

    # WHEN loading user info
    mock_app.test_client().post('/user', data=data)

    # The user should be added to the database
    assert mock_app.adapter.user_collection.estimated_document_count() == 1


def test_batch_valid_files(mock_app, valid_concentrations, valid_csv, segmental_calls, multiqc_report):
    # GIVEN:
    #   a valid csv file with three samples
    #   a valid concentrations file
    #   segmental_calls and multiqc_report files with random content, but that do exist.

    project_name = "Mamma"
    data = dict(multiqc_report=multiqc_report, segmental_calls=segmental_calls, result_file=valid_csv,
                concentrations=valid_concentrations, project_name=project_name)

    # WHEN loading the data
    mock_app.test_client().post('/load', data=data)

    # THEN assert the samples should be added to the sample collection
    # and the batch should be added to the batch collection
    assert mock_app.adapter.sample_collection.estimated_document_count() == 3
    assert mock_app.adapter.batch_collection.estimated_document_count() == 1



def test_batch_invalid_file(mock_app, valid_concentrations, invalid_csv, segmental_calls, multiqc_report):
    # GIVEN:
    #   a invalid csv file with three samples - required field SampleID has bad format
    #   a valid concentrations file
    #   segmental_calls and multiqc_report files with random content, but that do exist.

    project_name = "Mamma"
    data = dict(multiqc_report=multiqc_report, segmental_calls=segmental_calls, result_file=invalid_csv,
                concentrations=valid_concentrations, project_name=project_name)

    # WHEN loading the data
    mock_app.test_client().post('/load', data=data)

    # THEN assert nothing added to sample the collection
    assert mock_app.adapter.sample_collection.estimated_document_count() == 0

    # THEN assert batch collection added with expected keys
    keys = ['_id', 'multiqc_report', 'segmental_calls', 'fluffy_result_file', 'added']
    assert mock_app.adapter.batch_collection.estimated_document_count() == 1
    assert list(mock_app.adapter.batch(project_name).keys()) == keys


def test_batch_no_file(mock_app):
    # GIVEN

    # WHEN loading loading empty data
    # THEN assert Error raised
    with pytest.raises(NIPToolError):
        mock_app.test_client().post('/load', data=dict())

    # THEN assert nothing added to sample or batch collections
    # THEN assert Badly formated csv! Can not load. Exiting.
    assert mock_app.adapter.sample_collection.estimated_document_count() == 0
    assert mock_app.adapter.batch_collection.estimated_document_count() == 0

