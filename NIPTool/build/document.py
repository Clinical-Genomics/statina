from NIPTool.models.constants import SAMPLE_KEYS, BATCH_KEYS
from NIPTool.models.converters import convert


def build_document(csv_data: dict, document_keys: list) -> dict:

    document = {}
    for key in document_keys:
        value = csv_data.get(key)
        value = convert(key, value)
        if value is None:
            continue
        document[key] = value

    return document

def build_sample(sample_data: dict) -> dict:
    """Builds a document for the sample collection"""

    sample = build_document(sample_data, SAMPLE_KEYS)
    sample["_id"] = sample_data.get("SampleID")

    return sample


def build_batch(batch_data: dict) -> dict:
    """Builds a document for the batch collection"""

    batch = build_document(batch_data, BATCH_KEYS)
    batch["_id"] = str(batch_data.get('SampleProject'))
    
    return batch