from NIPTool.constants.constants import BATCH_KEYS


def build_batch(batch_data: dict):
    """Builds a document for the batch collection"""

    batch_document = {'_id': str(batch_data.get('SampleProject'))}
    for key in BATCH_KEYS:
        if batch_data.get(key) is not None:
            batch_document[key] = batch_data.get(key)
            
    return batch_document