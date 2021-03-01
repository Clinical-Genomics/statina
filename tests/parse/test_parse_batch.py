from pathlib import Path
from typing import List

from NIPTool.parse.batch import get_samples, parse_csv
import pytest	
from NIPTool.exeptions import MissingResultsError
from NIPTool.schemas.db_models.sample import SampleModel


def get_nr_csv_entries(csv_path: Path) -> int:
    lines = []
    with open(csv_path, "r") as infile:
        # Skip header
        next(infile)
        lines = [line for line in infile]
    return len(lines)


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

def test_parse_batch(valid_csv: Path):
    # GIVEN a valid csv file
    # GIVEN the number of samples
    nr_samples = get_nr_csv_entries(valid_csv)

    # WHEN running parse_batch_file
    results: List[SampleModel] = get_samples(valid_csv)

    # THEN assert results is a list and it has length 3
    assert isinstance(results, list)
    # THEN assert that the objects are samples
    assert isinstance(results[0], SampleModel)


def test_parse_batch_file_with_missing_data(invalid_csv):	
    # GIVEN a csv file with missing SampleID

    # WHEN running parse_batch_file
    results = get_samples(invalid_csv)

    # THEN assert results is a list and it has length 3
    assert isinstance(results, list)
    for sample in results:
        assert sample == {}
