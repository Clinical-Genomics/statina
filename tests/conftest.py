from pathlib import Path

import pytest

from mongomock import MongoClient
from .small_helpers import SmallHelpers
from NIPTool.server import create_app, configure_app
from NIPTool.adapter.plugin import NiptAdapter

from NIPTool.server.app.api.api_v1.api import app
from NIPTool.server.app.api.deps import get_nipt_adapter
from fastapi.testclient import TestClient

DATABASE = "testdb"

def override_dependency(db_client):
    return NiptAdapter(db_client, db_name=DATABASE)


@pytest.fixture(scope="function")
def database(request, pymongo_client):
    """Get an adapter connected to mongo database"""

    mongo_client = pymongo_client
    database = mongo_client[DATABASE]
    return database


@pytest.fixture()
def mock_fast_client(database):
    """Return a mock app"""

    client = TestClient(app)
    app.dependency_overrides[get_nipt_adapter] = override_dependency(database.client)

    return client



@pytest.fixture()
def mock_app(database):
    """Return a class with small helper functions"""
    app = create_app(test=True)
    app.db = database
    app.adapter = NiptAdapter(database.client, db_name=database.name)
    return app


@pytest.fixture(scope="function")
def pymongo_client(request):
    """Get a client to the mongo database"""

    mock_client = MongoClient()

    def teardown():
        mock_client.drop_database(DATABASE)

    request.addfinalizer(teardown)
    return mock_client





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

    return Path("tests/fixtures/valid_fluffy.csv")


@pytest.fixture
def invalid_csv():
    """Get file path to invalid csv"""

    return "tests/fixtures/not_a_valid_fluffy.csv"


@pytest.fixture
def multiqc_report():
    """Get file path to multiqc_report"""

    return "tests/fixtures/multiqc_report.html"

@pytest.fixture
def segmental_calls():
    """Get file path to segmental_calls"""

    return "tests/fixtures/segmental_calls"
