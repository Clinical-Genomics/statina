import logging
from NIPTool.build.document import build_sample, build_batch
from NIPTool.models.validation import requiered_fields
from pathlib import Path
from typing import Optional

LOG = logging.getLogger(__name__)


def check_requiered_fields(document):
    """Check if document keys contain required fields"""

    if not set(requiered_fields).issubset(set(document.keys())):
        LOG.info(f"Could not add document {document}. Requiered fields missing.")
        return False
    return True


def pars_segmental_calls(segmental_calls_path: Optional[str]) -> dict:
    """Builds a dict with segmental calls bed files.
        key: sample ids
        value: bed file path"""

    segmental_calls_dir = Path(segmental_calls_path)
    segmental_calls = {}
    if not segmental_calls_dir.exists():
        LOG.info('Segmental Calls file path missing.')
        return segmental_calls

    for file in segmental_calls_dir.iterdir():
        if file.suffix == '.bed':
            sample_id = file.name.split('.')[0]
            segmental_calls[sample_id] = str(file.absolute())

    return segmental_calls


def load_batch(adapter, batch_data: dict, request_data: dict) -> None:
    """Function to load data from fluffy result file."""

    mongo_batch = build_batch(batch_data, request_data)
    adapter.add_or_update_document(mongo_batch, adapter.batch_collection)


def load_samples(adapter, batch_data: list, request_data: dict) -> None:
    """Function to load data from fluffy result file."""

    segmental_calls = pars_segmental_calls(segmental_calls_path=request_data.get('segmental_calls'))
    for sample in batch_data:
        if not check_requiered_fields(sample):
            continue
        sample_id = sample["SampleID"]
        segmental_calls_path = segmental_calls.get(sample_id)
        mongo_sample = build_sample(sample_data=sample, segmental_calls=segmental_calls_path, sample_id=sample_id)

        adapter.add_or_update_document(mongo_sample, adapter.sample_collection)
