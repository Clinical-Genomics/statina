from NIPTool.constants.constants import SAMPLE_KEYS

def build_sample(sample_data: dict):
    """Builds a document for the sample collection"""

    sample = {'_id': sample_data.get('SampleID')}
    for key in SAMPLE_KEYS:
        if sample_data.get(key) is not None:
            sample[key] = sample_data[key]
    sample['SampleProject'] = str(sample['SampleProject'])

    return sample
