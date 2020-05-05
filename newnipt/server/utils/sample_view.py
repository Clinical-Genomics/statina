from newnipt.server.constants import *
from copy import deepcopy


def get_abnormal(adapter, chr, x_axis):
    plot_data = {}
    
    pipe = [{'$match': {
                f'status_T{chr}': {
                    '$ne': 'Normal', 
                    '$exists': 'True'
                    }, 
                'include': {'$eq': True}
            }},{"$group": {
                 "_id": {f"status_T{chr}": f"$status_T{chr}"},
                 "values": {"$push": f"$Zscore_{chr}"},
                 "names": {"$push": "$_id"},
                 "count": {"$sum": 1}
                 }}]

    for status_dict in adapter.sample_aggregate(pipe):
        status = status_dict['_id'][f'status_T{chr}']
        plot_data[status] = {'values': [ value for value in status_dict.get('values')],
                             'names': status_dict.get('names'),
                             'count': status_dict.get('count'),
                             'x_axis': [x_axis]*status_dict.get('count')}
    return plot_data



def get_normal(adapter, chr):
    pipe = [{'$match': {
                f'status_T{chr}': {'$eq': 'Normal'}, 
                'include': {'$eq': True}}
            },
            {"$group": {
                "_id": {f"status_T{chr}": f"$status_T{chr}"},
                "values": {"$push": f"$Zscore_{chr}"},
                "names": {"$push": "$_id"},
                "count": {"$sum": 1}
            }}]
    if not list(adapter.sample_aggregate(pipe)):
        return {}
    data = list(adapter.sample_aggregate(pipe))[0]
    data['values'] = [ value for value in data.get('values', [])]
    return data

def get_abn_for_samp_tris_plot(adapter):
    plot_data = {}
    data_per_abnormaliy = {}
    for status in STATUS_CLASSES:
        plot_data[status] = {'values': [],
                             'names': [],
                             'count': 0,
                             'x_axis': []} 
    x_axis = 1
    for abn in ["13", "18", "21"]:
        data = get_abnormal(adapter, abn, x_axis)
        data_per_abnormaliy[abn] = data

        for status, status_dict in data.items():
            plot_data[status]['values'] += status_dict.get('values', [])
            plot_data[status]['names'] += status_dict.get('names', [])
            plot_data[status]['count'] += status_dict.get('count', 0)
            plot_data[status]['x_axis'] += status_dict.get('x_axis', [])
        x_axis+=1

    return plot_data, data_per_abnormaliy

def get_normal_for_samp_tris_plot(adapter):
    data_per_abnormaliy = {}
    x_axis = 1
    for abn in ["13", "18", "21"]:
        data = get_normal(adapter, abn)
        data['x_axis'] = [x_axis]*data.get('count', 0)
        data_per_abnormaliy[abn] = data
        x_axis+=1
    return data_per_abnormaliy


def get_sample_for_samp_tris_plot(sample):
    return {"13":{'value': sample.get('Zscore_13') ,'x_axis': 1},
            "18":{'value': sample.get('Zscore_18') ,'x_axis': 2},
            "21":{'value': sample.get('Zscore_21'),'x_axis': 3}}
