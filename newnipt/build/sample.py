from newnipt.constants.constants import SAMPLE_KEYS

def build_sample(sample_data: dict):
    sample = {'_id': sample_data.get('SampleID')}
    for key in SAMPLE_KEYS:
        if sample_data.get(key) is not None:
            sample[key] = sample_data[key]
    sample['SampleProject'] = str(sample['SampleProject'])
    return sample
