from NIPTool.build.sample import build_sample
import pytest


def test_build_sample():
    # GIVEN a sample_data with requiered key 'SampleID'
    sample_data = {
        "SampleID": "2020-07452-02",
        "Description": " ",
        "SampleProject": 201862,
        "Zscore_13": -10.1836097044367,
    }

    # WHEN building a mongo sample
    mongo_sample = build_sample(sample_data=sample_data)

    # THEN the mongo_sample has a key "_id" with the value of "SampleID"
    assert mongo_sample == {
        "_id": "2020-07452-02",
        "SampleID": "2020-07452-02",
        "SampleProject": "201862",
        "Zscore_13": -10.1836097044367,
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
    assert mongo_sample == {"_id": "2020-07452-02", "SampleID": "2020-07452-02"}
