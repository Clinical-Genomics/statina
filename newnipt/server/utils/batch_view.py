from newnipt.server.constants import *
from copy import deepcopy

## Batch view

def get_sample_info(sample):
    
    z_score_13 = round(sample.get("Zscore_13"), 2)
    z_score_18 = round(sample.get("Zscore_18"), 2)
    z_score_21 = round(sample.get("Zscore_21"), 2)
    CNVSegment = sample.get("CNVSegment")
    FF = round(sample.get("FF_Formatted"),2)
    FFX = round(sample.get("FFX"),2)
    FFY = round(sample.get("FFY"),2)

    return {
        "sample_id": sample.get("_id"),
        "FF": {
            "value": FF,
            "warn": _get_ff_warning(FF),
        },
        "CNVSegment": {
            "value": CNVSegment,
            "warn": "default",
        },
        "FFX": {
            "value": FFX,
            "warn": "default",
        },
        "FFY": {
            "value": FFY,
            "warn": "default",
        },
        "Zscore_13": {
            "value": z_score_13,
            "warn": _get_tris_warning(z_score_13, FF),
        },
        "Zscore_18": {
            "value": z_score_18,
            "warn": _get_tris_warning(z_score_18, FF),
        },
        "Zscore_21": {
            "value": z_score_21,
            "warn": _get_tris_warning(z_score_21, FF),
        },
        "Zscore_X": {"value": round(sample.get("Zscore_X"),2)},
        #'Warning': 'value': _get_warnings(sample),
        "Status": _get_status(sample),
        "Include": sample.get("include"),
        "Comment": sample.get("comment", ''),
        "Last_Change": sample.get("change_include_date"),
    }


def _get_status(sample):
    """Get the manually defined sample status for batch table"""
    status_list = []
    for key in TRIS_CHROM_ABNORM + SEX_CHROM_ABNORM:
        status = sample.get(f"status_{key}")
        if status and status != "Normal":
            status_list.append(" ".join([status, key]))
    return ", ".join(status_list)


def _get_ff_warning(fetal_fraction):
    """Get fetal fraction warning based on preset treshold"""
    try:
        fetal_fraction = fetal_fraction
    except:
        fetal_fraction = None
    if fetal_fraction and fetal_fraction <= FF_TRESHOLD:
        return "danger"
    else:
        return "default"


def _get_tris_warning(z_score: float, fetal_fraction):
    """Get automated trisomi warning, based on preset Zscore thresholds"""

    if fetal_fraction <= 5:
        smax = TRISOMI_TRESHOLDS["soft_max_ff"]["NCV"]
    else:
        smax = TRISOMI_TRESHOLDS["soft_max"]["NCV"]
    hmin = TRISOMI_TRESHOLDS["hard_min"]["NCV"]
    hmax = TRISOMI_TRESHOLDS["hard_max"]["NCV"]
    smin = TRISOMI_TRESHOLDS["soft_min"]["NCV"]

    if (smax <= z_score < hmax) or (hmin < z_score <= smin):
        warn = "warning"
    elif (z_score >= hmax) or (z_score <= hmin):
        warn = "danger"
    else:
        warn = "default"
    return warn


def get_ff_abnormal(adapter):
    plot_data = {}
    for abn in SEX_CHROM_ABNORM:
        plot_data[abn] = {}
        pipe = [
            {'$match': {
                f'status_{abn}': {
                    '$ne': 'Normal', 
                    '$exists': 'True'
                    }, 
                'include': {'$eq': True}}},
            {"$group": {
                 "_id": {f"status_{abn}": f"$status_{abn}"},
                 "FFX": {"$push": "$FFX"},
                 "FFY": {"$push": "$FFY"},
                 "names": {"$push": "$_id"},
                 "count": {"$sum": 1}
                 }}]
        for status_dict in adapter.sample_aggregate(pipe):
            status = status_dict['_id'][f'status_{abn}']
            plot_data[abn][status] = status_dict
    return plot_data


def get_ff_control(adapter):
    pipe = [{
        '$match': {
            'FF_Formatted': {'$ne': 'None', '$exists': 'True'}, 
            'FFY': {'$ne': 'None', '$exists': 'True'}, 
            'FFX': {'$ne': 'None', '$exists': 'True' }, 
            'include': {'$eq': True}}
        }, {
        '$group': {
            '_id': 'None', 
            'FFY': {'$push': '$FFY'}, 
            'FFX': {'$push': '$FFX'}, 
            'FF': {'$push': '$FF_Formatted'}, 
            'names': {'$push': '$_id'}, 
            'count': {'$sum': 1}}
        }]
    return list(adapter.sample_aggregate(pipe))[0]


def get_ff_cases(adapter, batch_id):
    pipe = [{
        '$match': {
            'SampleProject': {'$eq': batch_id},
            'FF_Formatted': {'$ne': 'None', '$exists': 'True'}, 
            'FFY': {'$ne': 'None', '$exists': 'True'}, 
            'FFX': {'$ne': 'None', '$exists': 'True' }, 
            'include': {'$eq': True}}
        }, {
        '$group': {
            '_id': 'None', 
            'FFY': {'$push': '$FFY'}, 
            'FFX': {'$push': '$FFX'}, 
            'FF_Formatted': {'$push': '$FF_Formatted'}, 
            'names': {'$push': '$_id'}}
        }]
    data = list(adapter.sample_aggregate(pipe))[0]
    massaged_data = {}
    for i, sample_id in enumerate(data['names']):
        massaged_data[sample_id] = {'FFY': data['FFY'][i], 
                                    'FFX': data['FFX'][i], 
                                    'FF': data['FF_Formatted'][i]}
    return massaged_data



def get_case_data_for_batch_tris_plot(adapter, chr, batch_id):
    pipe = [{'$match': 
                {'SampleProject': {'$eq': batch_id},
                'include': {'$eq': True}}
                },
            {"$group": {
             "_id": {"batch": "$SampleProject"},
             "values": {"$push": f"$Zscore_{chr}"},
             "names": {"$push": "$_id"},
             "count": {"$sum": 1}
             }}]

    
    if not list(adapter.sample_aggregate(pipe)):
        return {}
    
    data = list(adapter.sample_aggregate(pipe))[0]
    data['values'] = [ value for value in data.get('values')]
    data['x_axis'] = list(range(1,data.get('count')+1))
    return data


def get_data_for_coverage_plot(samples):
    data = {}
    for sample in samples:
        sample_id = sample['_id']
        data[sample_id] = []
        for i in range(1, 23):
            data[sample_id].append(sample.get(f'Chr{str(i)}_Ratio', 0)) 
    return data
