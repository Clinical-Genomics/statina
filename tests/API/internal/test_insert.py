import pytest
from fastapi import status
from pydantic import ValidationError

"""
def test_user_mocked(mocker, fast_app_client, valid_load_user):
    # GIVEN a insert_user function that never fails
    mocker.patch('statina.server.load.api.api_v1.endpoints.load.insert_user')

    # WHEN running the user request with the data
    response = fast_app_client.post('/api/v1/insert/user', json=valid_load_user.dict())

    assert response.status_code == status.HTTP_200_OK


def test_user_load_fails_mocked(mocker, mock_fast_client):
    # GIVEN the following request data:
    data = dict(email='maya.papaya@something.se', name="Maya Papaya", role="RW")

    with patch('statina.server.load.api.api_v1.endpoints.load.insert_user', side_effect=Exception('mocked error')):
        # WHEN running the user request with the data
        response = mock_fast_client.post('/api/v1/insert/user', json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY"""


# def test_user(fast_app_client, valid_load_user):
#     # GIVEN valid user load data
#
#     # WHEN running the user request with the data
#     response = fast_app_client.post("/api/v1/insert/user", json=valid_load_user.dict())
#
#     # THEN
#     assert "inserted to the database" in response.text
#     assert response.status_code == status.HTTP_200_OK


# def test_user_wrong_input(fast_app_client, valid_load_user):
#     # GIVEN user data with missing email field
#     data = valid_load_user.dict()
#     data.pop("email")
#
#     # WHEN running the user request with the data
#     response = fast_app_client.post("/api/v1/insert/user", json=data)
#
#     # THEN
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# def test_batch_valid_files(fast_app_client, valid_load_batch):
#     # GIVEN the valid load batch data
#
#     # WHEN running the request with the data
#     response = fast_app_client.post("/api/v1/insert/batch", json=valid_load_batch.dict())
#
#     # THEN
#     assert "inserted to the database" in response.text
#     assert response.status_code == status.HTTP_200_OK


# def test_batch_wrong_segmental_calls_path(fast_app_client, valid_load_batch):
#     # GIVEN the following request data:
#     #   a valid csv file with three samples
#     #   but no segmental_calls and multiqc_report
#
#     data = valid_load_batch.dict()
#     data["segmental_calls"] = "no_valid_path"
#
#     # WHEN running the request with the data
#     response = fast_app_client.post("/api/v1/insert/batch", json=data)
#
#     # THEN assert batch is being added without error
#     assert "inserted to the database" in response.text
#     assert response.status_code == status.HTTP_200_OK


# def test_batch_wrong_result_file_path(fast_app_client, valid_load_batch):
#     # GIVEN the following request data:
#
#     data = valid_load_batch.dict()
#     data["result_file"] = "no_valid_path"
#
#     # WHEN running the request with the data
#     response = fast_app_client.post("/api/v1/insert/batch", json=data)
#
#     # THEN assert
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     assert "Results file missing" in response.text


# def test_batch_no_data(fast_app_client):
#     # GIVEN no data
#
#     # WHEN running the request with empty data
#     response = fast_app_client.post("/api/v1/insert/batch", json=dict())
#
#     # THEN assert BadRequestKeyError: 400 Bad Request
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# def test_batch_invalid_file(fast_app_client, valid_load_batch, csv_with_missing_sample_id):
#     # GIVEN batch load data with a csv result file with missing sample ids:
#     data = valid_load_batch.dict()
#     data["result_file"] = csv_with_missing_sample_id
#
#     # WHEN running the request with the data
#     # THEN assert ValidationError and "Required fields missing" in response message
#     with pytest.raises(ValidationError):
#         response = fast_app_client.post("/api/v1/insert/batch", json=data)
#         assert "Could not load data from result file. Required fields missing." in response.text
