from newnipt.constants.constants import BATCH_KEYS


def build_batch(batch_data: dict):
    batch = {'_id': batch_data.get('Flowcell')}
    for key in BATCH_KEYS:
        batch[key] = batch_data.get(key)
    return batch