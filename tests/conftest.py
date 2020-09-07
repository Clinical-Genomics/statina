import pytest

from mongomock import MongoClient

DATABASE = 'testdb'

@pytest.fixture(scope='function')
def pymongo_client(request):
    """Get a client to the mongo database"""
    
    mock_client = MongoClient()

    def teardown():
        mock_client.drop_database(DATABASE)

    request.addfinalizer(teardown)
    return mock_client


@pytest.fixture(scope='function')
def database(request, pymongo_client):
    """Get an adapter connected to mongo database"""

    mongo_client = pymongo_client
    database = mongo_client[DATABASE]
    return database


##########################################
###### fixture files for input csv ######
##########################################


@pytest.fixture
def valid_csv():
    """Get file path to valid csv"""
    
    return 'tests/fixtures/valid_fluffy.csv'


@pytest.fixture
def invalid_csv():
    """Get file path to invalid csv"""

    return 'tests/fixtures/not_a_valid_fluffy.csv'