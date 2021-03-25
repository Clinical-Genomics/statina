from pathlib import Path
from typing import List
from pydantic import ValidationError
import pytest
from NIPTool.parse.batch import get_samples, get_batch, parse_csv, pars_segmental_calls
from NIPTool.models.database import Sample, Batch


def get_nr_csv_entries(csv_path: Path) -> int:
    lines = []
    with open(csv_path, "r") as infile:
        # Skip header
        next(infile)
        lines = [line for line in infile]
    return len(lines)


def test_parse_segmental_calls(segmental_calls: str):
    # GIVEN a result files directory with 3 segmental calls files
    # WHEN running pars_segmental_calls
    result = pars_segmental_calls(segmental_calls)

    # THEN assert that the result is a dict
    assert isinstance(result, dict)

    # The dict contains three elements
    assert len(result.keys()) == 3


def test_parse_segmental_calls_no_path(caplog):
    # GIVEN a non existing result files directory
    path = "non_existing_path"

    # WHEN running pars_segmental_calls
    result = pars_segmental_calls(path)

    # THEN assert a waring about missing path is being logged
    assert 'Segmental Calls file path missing' in caplog.text

    # THEN assert that the result is a empty dict
    assert result == {}


def test_parse_csv(valid_csv: Path):
    # GIVEN a csv file
    # GIVEN the number of samples
    nr_samples = get_nr_csv_entries(valid_csv)

    # WHEN parsing the file into a list of dicts
    result = parse_csv(valid_csv)

    # THEN assert that the result is a list of dicts
    assert isinstance(result, list)
    # THEN assert the correct nr of samples was parsed
    assert len(result) == nr_samples


def test_get_samples(valid_csv: Path):
    # GIVEN a valid csv file
    # GIVEN the number of samples
    nr_samples = get_nr_csv_entries(valid_csv)

    # WHEN running get_samples
    results: List[Sample] = get_samples(valid_csv)

    # THEN assert results is a list and it has length 3
    assert isinstance(results, list)
    # THEN assert that the objects are samples
    assert isinstance(results[0], Sample)


def test_get_samples_with_missing_sample_id_in_csv(csv_with_missing_sample_id):
    # GIVEN a csv file with missing SampleID

    # WHEN running get_samples
    # THEN pydantic ValidationError is being raised
    with pytest.raises(ValidationError):
        get_samples(csv_with_missing_sample_id)


def test_get_batch(valid_csv: Path):
    # GIVEN a valid csv file

    # WHEN running get_samples
    results: Batch = get_batch(valid_csv)

    # THEN assert that the objects are samples
    assert isinstance(results, Batch)


def test_get_batch_with_missing_sample_project_in_csv(csv_with_missing_sample_project):
    # GIVEN a csv file with missing SampleID

    # WHEN running get_samples
    # THEN pydantic ValidationError is being raised
    with pytest.raises(ValidationError):
        get_batch(csv_with_missing_sample_project)
