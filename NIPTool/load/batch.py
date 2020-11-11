import logging
from NIPTool.build.document import build_sample, build_batch
from NIPTool.parse.batch import parse_batch_file
from NIPTool.models.validation import requiered_fields


LOG = logging.getLogger(__name__)


def check_requiered_fields(document):
    """Check if document keys contain requiered fields"""

    if not set(requiered_fields).issubset(set(document.keys())):
        LOG.info(f"Could not add document {document}. Requiered fields missing.")
        return False
    return True


def load_result_file(adapter, batch_data: list) -> None:
    """Function to load data from fluffy result file. 
    Raises:
        MissingResultsError: when parsing file that is empty"""

    batch_data = parse_batch_file(batch_data)

    for sample in batch_data:
        if not check_requiered_fields(sample):
            continue
        mongo_sample = build_sample(sample)
        adapter.add_or_update_document(mongo_sample, adapter.sample_collection)

    if not check_requiered_fields(batch_data[0]):
        return
    mongo_batch = build_batch(batch_data[0])
    adapter.add_or_update_document(mongo_batch, adapter.batch_collection)


def load_concentrastions(adapter, concentrations: dict) -> None:
    """Function to load concentrations to samples in the database."""

    for sample, concentration in concentrations.items():
        mongo_sample = adapter.sample(sample)
        mongo_sample["concentration"] = concentration
        adapter.add_or_update_document(mongo_sample, adapter.sample_collection)


def load_project_name(adapter, project_name: str, flowcell: str) -> None:
    """Function to load batch name"""

    mongo_batch = adapter.batch(flowcell)
    mongo_batch["SampleProject"] = project_name
    adapter.add_or_update_document(mongo_batch, adapter.batch_collection)

