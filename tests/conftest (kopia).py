from pathlib import Path
import pytest
from mongomock import MongoClient
from .small_helpers import SmallHelpers
from NIPTool.server import create_app, configure_app
from NIPTool.schemas.server.load import UserLoadModel

from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.server.load.api.api_v1.api import app
from NIPTool.server.load.api.deps import get_nipt_adapter
from fastapi.testclient import TestClient

DATABASE = "testdb"


def override_nipt_adapter():
    """Function for overriding the nipt adapter dependency"""

    mongo_client = MongoClient()
    database = mongo_client[DATABASE]
    adapter = NiptAdapter(database.client, db_name=DATABASE)
    return adapter


@pytest.fixture()
def fast_app_client():
    """Return a mock fastapi app"""

    client = TestClient(app)
    app.dependency_overrides[get_nipt_adapter] = override_nipt_adapter
    return client



@pytest.fixture(scope="function")
def pymongo_client(request):
    """Get a client to the mongo database"""

    mongo_client = MongoClient()

    def teardown():
        mongo_client.drop_dTestClientatabase(DATABASE)

    request.addfinalizer(teardown)
    return mongo_client


@pytest.fixture(scope="function")
def database(request, pymongo_client):
    """Get an adapter connected to mongo database"""

    mongo_client = pymongo_client
    database = mongo_client[DATABASE]
    return database

@pytest.fixture(scope="function")
def valid_load_user():
    user = UserLoadModel(email='maya.papaya@something.se', name="Maya Papaya", role="RW")
    return user



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
