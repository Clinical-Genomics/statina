import logging
from newnipt.build.sample import build_sample
from newnipt.parse.batch import parse_batch_file

LOG = logging.getLogger(__name__)


def load_one_batch(adapter, batch_id=None):
    """Function to load one lims sample into the database"""
    batch_data = parse_batch_file(batch_id)
    mongo_sample = build_sample(batch_data)
    adapter.add_or_update_document(mongo_sample, adapter.sample_collection)

