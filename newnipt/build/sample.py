from newnipt.constants.constants import SAMPLE_KEYS

def build_sample(sample_data: dict):
    sample = {'_id': sample_data.get('SampleID')}
    for key in SAMPLE_KEYS:
        sample[key] = sample_data.get(key)
    return sample
