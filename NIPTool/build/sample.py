from NIPTool.constants.constants import SAMPLE_KEYS

def build_sample(sample_data: dict):
    """Builds a document for the sample collection"""


    sample = {'_id': sample_data.get('SampleID')}
    
    for key in SAMPLE_KEYS:
        value = sample_data.get(key)
        if isinstance(value, str) and not value.strip():
            continue
        if value is None:
            continue
        sample[key] = value
    
    if sample.get('SampleProject'):
        sample['SampleProject'] = str(sample['SampleProject'])

    return sample
