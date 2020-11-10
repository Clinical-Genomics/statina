import logging
from NIPTool.build.document import build_sample, build_batch
from NIPTool.parse.batch import parse_batch_file
from NIPTool.models.validation import requiered_fields
import json


LOG = logging.getLogger(__name__)


def check_requiered_fields(document):
    """Check if document keys contain requiered fields"""

    if not set(requiered_fields).issubset(set(document.keys())):
        LOG.info(f"Could not add document {document}. Requiered fields missing.")
        return False
    return True


def load_one_batch(adapter, load_config_path: str):
    """Function to load one lims sample into the database. 
    Raises:
        MissingResultsError: when parsing file that is empty"""
    # kanske separera momentetn i tre funktioner för enklare testning
    # läs dict inte fil
    with open(load_config_path) as file:
        config_data = json.load(file)

    batch_data = parse_batch_file(config_data["result_file"])
    concentrations = config_data["concentrations"]
    project_name = config_data["project_name"]

    for sample in batch_data:
        if not check_requiered_fields(sample):
            continue
        mongo_sample = build_sample(sample)
        mongo_sample["concentration"] = concentrations[mongo_sample["_id"]]
        adapter.add_or_update_document(mongo_sample, adapter.sample_collection)

    if not check_requiered_fields(batch_data[0]):
        return
    mongo_batch = build_batch(batch_data[0])
    mongo_batch["SampleProject"] = project_name
    adapter.add_or_update_document(mongo_batch, adapter.batch_collection)
