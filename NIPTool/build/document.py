from NIPTool.models.constants import SAMPLE_KEYS, BATCH_KEYS
from typing import Optional

def empty_str_to_none(x: str) -> Optional[str]:
    """Convert empty string to None"""

    x = x.strip()
    if not x:
        return None
    return x


def build_document(csv_data: dict, document_keys: list) -> dict:
    """Build a general document"""

    document = {}
    for key in document_keys:
        value = csv_data.get(key)
        if isinstance(value, str):
            value = empty_str_to_none(value)
        if value is None:
            continue
        document[key] = value

    return document


def build_sample(sample_data: dict) -> dict:
    """Builds a document for the sample collection"""

    sample = build_document(sample_data, SAMPLE_KEYS)
    if sample.get("SampleProject"):
        sample["SampleProject"] = str(sample["SampleProject"])
    sample["_id"] = sample_data["SampleID"]

    return sample


def build_batch(batch_data: dict) -> dict:
    """Builds a document for the batch collection"""

    batch = build_document(batch_data, BATCH_KEYS)
    batch["_id"] = str(batch_data.get("SampleProject"))

    return batch
