from NIPTool.build.document import build_batch
from NIPTool.models.constants import BATCH_KEYS
import pytest


def test_build_batch():
    # GIVEN a batch_data with requiered key 'SampleProject'
    batch_data = {
        "Median_18": 1.01950547134618,
        "SampleProject": 201862,
        "Stdev_13": 0.009517510060085,
    }

    # WHEN building a mongo batch
    mongo_batch = build_batch(batch_data=batch_data)

    # THEN the mongo_batch has a key "_id" with the value of "SampleProject"
    assert mongo_batch == {
        "_id": "201862",
        "Median_18": 1.01950547134618,
        "Stdev_13": 0.009517510060085,
    }


def test_build_batch_wrong_keys():
    # GIVEN a batch_data with not accepted keys: key1 key2 key3
    batch_data = {
        "SampleProject": 201862,
        "key1": " ",
        "key2": 201862,
        "key3": -10.1836097044367,
    }

    # WHEN building a mongo batch
    mongo_batch = build_batch(batch_data=batch_data)

    # THEN the unaccepted keys will not be part of the mongo_batch"
    assert mongo_batch == {"_id": "201862"}


@pytest.mark.parametrize("batch_key", BATCH_KEYS)
def test_build_batch_str_values(batch_key):
    # GIVEN a batch_data dict with requiered key 'SampleProject' and a batch_key with some str value
    batch_data = {"SampleProject": 201862, batch_key: "Value"}

    # WHEN building a mongo batch
    mongo_batch = build_batch(batch_data=batch_data)

    # THEN the the batch_key will be loaded into the mongo_batch dict
    assert mongo_batch == {"_id": "201862", batch_key: "Value"}


@pytest.mark.parametrize("batch_key", BATCH_KEYS)
def test_build_batch_zero_values(batch_key):
    # GIVEN a batch_data dict with requiered key 'SampleProject' and a batch_key with value 0
    batch_data = {"SampleProject": 201862, batch_key: 0}

    # WHEN building a mongo batch
    mongo_batch = build_batch(batch_data=batch_data)

    # THEN the the batch_key will be loaded into the mongo_batch dict
    assert mongo_batch == {"_id": "201862", batch_key: 0}


@pytest.mark.parametrize("batch_key", BATCH_KEYS)
def test_build_batch_empty_strings(batch_key):
    # GIVEN a batch_data dict with requiered key 'SampleProject' and a batch_key with empty string as value
    batch_data = {"SampleProject": 201862, batch_key: " "}

    # WHEN building a mongo batch
    mongo_batch = build_batch(batch_data=batch_data)

    # THEN the the batch_key will not be loaded into the mongo_batch dict
    assert mongo_batch == {"_id": "201862"}