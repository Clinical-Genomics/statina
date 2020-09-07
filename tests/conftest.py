import pytest


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