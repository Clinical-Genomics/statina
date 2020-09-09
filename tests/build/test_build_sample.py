from NIPTool.build.document import build_sample
from NIPTool.models.constants import SAMPLE_KEYS
import pytest


def test_build_sample():
    # GIVEN a sample_data with requiered key 'SampleID'
    sample_data = {
        "SampleID": "2020-07452-02",
        "Description": " ",
        "Zscore_13": -10.1836097044367,
    }

    # WHEN building a mongo sample
    mongo_sample = build_sample(sample_data=sample_data)

    # THEN the mongo_sample has a key "_id" with the value of "SampleID"
    assert mongo_sample == {
        "_id": "2020-07452-02",
        "Zscore_13": -10.1836097044367,
    }


def test_build_sample_SampleProject_key():
    # GIVEN a sample_data with requiered key 'SampleID' and 'SampleProject' in int format
    sample_data = {
        "SampleID": "2020-07452-02",
        "SampleProject": 201862,
    }

    # WHEN building a mongo sample
    mongo_sample = build_sample(sample_data=sample_data)

    # THEN the value of "SampleProject" is in str format
    assert mongo_sample == {
        "_id": "2020-07452-02",
        "SampleProject": "201862",
    }


def test_build_sample_wrong_keys():
    # GIVEN a sample_data with not accepted keys: key1 key2 key3
    sample_data = {
        "SampleID": "2020-07452-02",
        "key1": " ",
        "key2": 201862,
        "key3": -10.1836097044367,
    }

    # WHEN building a mongo sample
    mongo_sample = build_sample(sample_data=sample_data)

    # THEN the unaccepted keys will not be part of the mongo_sample"
    assert mongo_sample == {"_id": "2020-07452-02"}


@pytest.mark.parametrize("sample_key", SAMPLE_KEYS)
def test_build_sample_str_values(sample_key):
    # GIVEN a sample_data dict with requiered key 'SampleID' and a sample_key with some str value
    sample_data = {"SampleID": "2020-07452-02", sample_key: "Value"}

    # WHEN building a mongo sample
    mongo_sample = build_sample(sample_data=sample_data)

    # THEN the the sample_key will be loaded into the mongo_sample dict
    if sample_key == "SampleID":
        assert mongo_sample == {"_id": "2020-07452-02", sample_key: "Value"}


@pytest.mark.parametrize("sample_key", SAMPLE_KEYS)
def test_build_sample_empty_strings(sample_key):
    # GIVEN a sample_data dict with requiered key 'SampleID' and a sample_key with empty string as value
    sample_data = {"SampleID": "2020-07452-02", sample_key: " "}

    # WHEN building a mongo sample
    mongo_sample = build_sample(sample_data=sample_data)

    # THEN the the sample_key will not be loaded into the mongo_sample dict
    assert mongo_sample == {"_id": "2020-07452-02"}


@pytest.mark.parametrize("sample_key", SAMPLE_KEYS)
def test_build_sample_zero_values(sample_key):
    # GIVEN a sample_data dict with requiered key 'SampleID' and a sample_key with value 0
    sample_data = {"SampleID": "2020-07452-02", sample_key: 0}

    # WHEN building a mongo sample
    mongo_sample = build_sample(sample_data=sample_data)

    # THEN the the sample_key will be loaded into the mongo_sample dict
    assert mongo_sample == {"_id": "2020-07452-02", sample_key: 0}
