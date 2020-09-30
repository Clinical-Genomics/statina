import pytest

from mongomock import MongoClient

DATABASE = "testdb"


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


def batch(
    batch_id = "201860",
    sequencing_date = "2022-03-10",
    stdev_13= 0.0095,
    stdev_18 = 0.0035,
    stdev_21 = 0.0085,
):
    """A batch mock"""

    return {
        "_id": batch_id,
        "SequencingDate": sequencing_date,
        "Median_13": 0.994623404680424,
        "Median_18": 1.01950547134618,
        "Median_21": 1.00710552415657,
        "Median_X": 0.8408228472301729,
        "Median_Y": 0.00011224982090899999,
        "Stdev_13": stdev_13,
        "Stdev_18": stdev_18,
        "Stdev_21": stdev_21,
        "Stdev_X": 0.029800076293786,
        "Stdev_Y": 0.0000653186791196846,
    }


def sample(
    batch_id: str = "201860",
    sample_id: str = "2020-07452-02",
    ratio_13: float = 0.97,
    ratio_18: float = 0.87,
    fetal_fraction: float = 11.5,
):
    """A sample mock"""

    return {
        "_id": sample_id,
        "SampleID": sample_id,
        "SampleType": "",
        "Description": "",
        "SampleProject": batch_id,
        "Index1": "CTACGAAG",
        "Index2": "CTCGACAG",
        "Library_nM": "",
        "QCFlag": "",
        "Zscore_13": 10.1836097044367,
        "Zscore_18": 14.2869756828577,
        "Zscore_21": 2.71403500910501,
        "Zscore_X": 31.293635764028803,
        "Ratio_13": ratio_13,
        "Ratio_18": ratio_18,
        "Ratio_21": 1.0105402184799999,
        "Ratio_X": 0.85445334198,
        "Ratio_Y": 0.0000711090401026516,
        "MappedReads": 29855557,
        "GC_Dropout": 0.000172,
        "AT_Dropout": 44.723144,
        "Chr1_Ratio": 0.992293808478,
        "Chr2_Ratio": 1.0065908236399999,
        "Chr3_Ratio": 0.974151095888,
        "Chr4_Ratio": 1.10624166283,
        "Chr5_Ratio": 1.0035390122299999,
        "Chr6_Ratio": 1.03661992778,
        "Chr7_Ratio": 1.0604126148100002,
        "Chr8_Ratio": 0.987816483295,
        "Chr9_Ratio": 1.00004978895,
        "Chr10_Ratio": 0.984502658354,
        "Chr11_Ratio": 0.949426097179,
        "Chr12_Ratio": 1.0228564842799999,
        "Chr14_Ratio": 0.988492203388,
        "Chr15_Ratio": 0.9931196645579999,
        "Chr16_Ratio": 0.9728049597669999,
        "Chr17_Ratio": 1.04339140264,
        "Chr19_Ratio": 1.05685913186,
        "Chr20_Ratio": 0.917316392889,
        "Chr22_Ratio": 1.05769882843,
        "Chr1": 1641640,
        "Chr2": 1456893,
        "Chr3": 1089600,
        "Chr4": 873556,
        "Chr5": 968727,
        "Chr6": 949012,
        "Chr7": 1005851,
        "Chr8": 851501,
        "Chr9": 797378,
        "Chr10": 949427,
        "Chr11": 853961,
        "Chr12": 853961,
        "Chr13": 478503,
        "Chr14": 593269,
        "Chr15": 614267,
        "Chr16": 749565,
        "Chr17": 837952,
        "Chr18": 439127,
        "Chr19": 714656,
        "Chr20": 555672,
        "Chr21": 250072,
        "Chr22": 451194,
        "ChrX": 758991,
        "ChrY": 2123,
        "FF_Formatted": fetal_fraction,
        "FFY": 0,
        "FFX": 13.14,
        "DuplicationRate": 0.0853080382992,
        "Bin2BinVariance": 0.054260164076747,
        "UnfilteredCNVcalls": 44,
        "CNVSegment": "Found",
        "comment": "None",
    }


##########################################
###### fixture files for input csv ######
##########################################


@pytest.fixture
def valid_csv():
    """Get file path to valid csv"""

    return "tests/fixtures/valid_fluffy.csv"


@pytest.fixture
def invalid_csv():
    """Get file path to invalid csv"""

    return "tests/fixtures/not_a_valid_fluffy.csv"
