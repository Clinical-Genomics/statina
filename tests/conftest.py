from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from mongomock import MongoClient

from statina.adapter.plugin import StatinaAdapter
from statina.config import get_nipt_adapter
from statina.main import internal_app as app
from statina.models.server.load import BatchRequestBody, UserRequestBody

from .small_helpers import SmallHelpers

DATABASE = "testdb"


def override_nipt_adapter():
    """Function for overriding the statina adapter dependency"""

    mongo_client = MongoClient()
    database = mongo_client[DATABASE]
    return StatinaAdapter(database.client, db_name=DATABASE)


@pytest.fixture()
def fast_app_client():
    """Return a mock fastapi app"""

    client = TestClient(app)
    app.dependency_overrides[get_nipt_adapter] = override_nipt_adapter
    return client


#####################


@pytest.fixture(scope="function")
def pymongo_client(request):
    """Get a client to the mongo database"""

    mock_client = MongoClient()

    def teardown():
        mock_client.drop_database(DATABASE)

    request.addfinalizer(teardown)
    return mock_client


@pytest.fixture(scope="function")
def database(request, pymongo_client):
    """Get an adapter connected to mongo database"""

    mongo_client = pymongo_client
    database = mongo_client[DATABASE]
    return database


@pytest.fixture(scope="function")
def valid_load_user():
    return UserRequestBody(
        email="maya.papaya@something.se",
        username="Maya Papaya",
        role="RW",
        password="123",
    )


@pytest.fixture(scope="function")
def valid_load_batch(multiqc_report, segmental_calls, valid_csv):
    batch_files = BatchRequestBody(
        multiqc_report=multiqc_report, segmental_calls=segmental_calls, result_file=valid_csv
    )
    return batch_files


@pytest.fixture(name="small_helpers")
def fixture_small_helpers():
    """Return a class with small helper functions"""
    return SmallHelpers()


##########################################
###### fixture files for input csv ######
##########################################


@pytest.fixture
def valid_csv() -> Path:
    """Get file path to valid csv"""

    return "tests/fixtures/fluffy_result_files/valid_fluffy.csv"


@pytest.fixture
def csv_with_missing_sample_id():
    """Get file path to invalid csv"""

    return "tests/fixtures/fluffy_result_files/fluffy_file_with_missing_sample_id.csv"


@pytest.fixture
def csv_with_missing_sample_project():
    """Get file path to invalid csv"""

    return "tests/fixtures/fluffy_result_files/fluffy_file_with_missing_sample_project.csv"


@pytest.fixture
def multiqc_report():
    """Get file path to multiqc_report"""

    return "tests/fixtures/fluffy_result_files/multiqc_report.html"


@pytest.fixture
def segmental_calls():
    """Get file path to segmental_calls"""

    return "tests/fixtures/fluffy_result_files"
