import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import parse_obj_as

from statina.models.database import Batch, DataBaseSample

LOG = logging.getLogger(__name__)


def parse_segmental_calls(segmental_calls_path: Optional[str]) -> dict:
    """Builds a dict with segmental calls bed files.
    key: sample ids
    value: bed file path"""

    segmental_calls = {}
    if not validate_file_path(segmental_calls_path):
        LOG.warning("Segmental Calls file path missing.")
        return segmental_calls

    segmental_calls_dir = Path(segmental_calls_path)
    for file in segmental_calls_dir.iterdir():
        if file.suffix == ".bed":
            sample_id = file.name.split(".")[0]
            segmental_calls[sample_id] = str(file.absolute())

    return segmental_calls


def validate_file_path(file_path: Optional[str]) -> bool:
    """File path validation"""

    if not file_path:
        return False
    file = Path(file_path)
    return file.exists()


def convert_empty_str_to_none(data: dict) -> dict:
    """Convert all values that are empty string to None in a dict"""

    for key, value in data.items():
        if not value:
            data[key] = None
    return data


def parse_csv(infile: Path) -> List[Dict[str, str]]:
    with open(infile, "r") as csv_file:
        entries = [convert_empty_str_to_none(entry) for entry in csv.DictReader(csv_file)]
    return entries


def get_samples(nipt_results_path: Path) -> List[DataBaseSample]:
    """Parse NIPT result file into samples"""

    return parse_obj_as(List[DataBaseSample], parse_csv(nipt_results_path))


def get_batch(nipt_results_path: Path) -> Batch:
    """Parse NIPT result file and create a batch object from the first sample information"""

    sample_data: List[dict] = parse_csv(nipt_results_path)

    return Batch.parse_obj(sample_data[0])
