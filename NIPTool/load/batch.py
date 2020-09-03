import logging
from NIPTool.build.sample import build_sample
from NIPTool.build.batch import build_batch
from NIPTool.parse.batch import parse_batch_file

LOG = logging.getLogger(__name__)


def load_one_batch(adapter, nipt_results_path:str):
    """Function to load one lims sample into the database. 
    Raises:
        MissingResultsError: when parsing file that is empty"""
    
    batch_data = parse_batch_file(nipt_results_path)
    for sample in batch_data:
        mongo_sample = build_sample(sample)
        adapter.add_or_update_document(mongo_sample, adapter.sample_collection)
    mongo_batch = build_batch(batch_data[0])
    adapter.add_or_update_document(mongo_batch, adapter.batch_collection)
