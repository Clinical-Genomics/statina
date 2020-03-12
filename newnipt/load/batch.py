import logging
from newnipt.build.sample import build_sample
from newnipt.build.batch import build_batch
from newnipt.parse.batch import parse_batch_file

LOG = logging.getLogger(__name__)


def load_one_batch(adapter, analysis_path, batch_id=None):
    """Function to load one lims sample into the database"""
    batch_data = parse_batch_file(batch_id, analysis_path)
    for sample in batch_data:
        mongo_sample = build_sample(sample)
        adapter.add_or_update_document(mongo_sample, adapter.sample_collection)
    mongo_batch = build_batch(batch_data[0])
    adapter.add_or_update_document(mongo_batch, adapter.batch_collection)

