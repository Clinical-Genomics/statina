from NIPTool.models.constants import SAMPLE_KEYS
from NIPTool.models.converters import CONVERTERS


def convert(key, value):
    """Convert values according to the converter model"""

    if value is None:
        return value

    for function, keys in CONVERTERS.items():
        if key in keys:
            return function(value)

    return value


def build_sample(sample_data: dict):
    """Builds a document for the sample collection"""

    sample = {"_id": sample_data.get("SampleID")}

    for key in SAMPLE_KEYS:
        value = sample_data.get(key)
        value = convert(key, value)
        if value is None:
            continue
        sample[key] = value

    return sample
