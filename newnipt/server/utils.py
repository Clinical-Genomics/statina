from newnipt.server.constants import *
from copy import deepcopy


def get_sample_info(sample):
    fetal_fraction = float(sample.get("FF_Formatted").rstrip("%").lstrip("<"))
    z_score_13 = float(sample.get("Zscore_13").replace(",", ".").replace("−", ""))
    z_score_18 = float(sample.get("Zscore_18").replace(",", ".").replace("−", ""))
    z_score_21 = float(sample.get("Zscore_21").replace(",", ".").replace("−", ""))
    return {
        "sample_id": sample.get("_id"),
        "FF_Formatted": {
            "value": fetal_fraction,
            "warn": _get_ff_warning(fetal_fraction),
        },
        "Zscore_13": {
            "value": z_score_13,
            "warn": _get_tris_warning(z_score_13, fetal_fraction),
        },
        "Zscore_18": {
            "value": z_score_18,
            "warn": _get_tris_warning(z_score_18, fetal_fraction),
        },
        "Zscore_21": {
            "value": z_score_21,
            "warn": _get_tris_warning(z_score_21, fetal_fraction),
        },
        "Zscore_X": {"value": sample.get("Zscore_X")},
        #'Warning': 'value': _get_warnings(sample),
        "Status": _get_status(sample),
        "Include": sample.get("include"),
        "Comment": sample.get("comment"),
        "Last_Change": sample.get("change_include_date"),
    }


def _get_status(sample):
    """Get the manually defined sample status"""
    status_list = []
    for key in ["T13", "T18", "T21", "X0", "XXX", "XXY", "XYY"]:
        status = sample.get(f"status_{key}")
        if status != "Normal":
            status_list.append(" ".join([status, key]))
    return ", ".join(status_list)


def _get_ff_warning(fetal_fraction):
    """Get fetal fraction warning based on preset treshold"""
    try:
        fetal_fraction = float(fetal_fraction.rstrip("%").lstrip("<"))
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


#################sample view


def get_tris_abn_for_plot(adapter):
    abnormalities = {}
    for status in STATUS_CLASSES:
        abnormalities[status] = {'values': [],
                                 'names': [],
                                 'count': 0,
                                 'x_axis': []} 

    for abn in ["13", "18", "21"]:
        pipe = [{"$group": {
                 "_id": {f"status_T{abn}": f"$status_T{abn}"},
                 "values": {"$push": f"$Zscore_{abn}"},
                 "names": {"$push": "$_id"},
                 "count": {"$sum": 1}
                 }}]

        for status_dict in adapter.sample_aggregate(pipe):
            status = status_dict['_id'][f'status_{abn}']

            abnormalities[status]['values'] += status_dict.get('values')
            abnormalities[status]['names'] += status_dict.get('names')
            abnormalities[status]['count'] += status_dict.get('count')
            abnormalities[status]['x_axis'] += 5

    return abnormalities



# NCV_classified={u'test-2020-07892-06_AHCKMCBCX3': 'T18', u'test-2020-07887-06_AHCKMCBCX3': '', u'test-2020-07897-06_AHCKMCBCX3': '', u'test-2020-07893-06_AHCKMCBCX3': '', u'test-2020-07890-06_AHCKMCBCX3': '', u'test-2020-07886-06_AHCKMCBCX3': '', u'test-2020-07889-06_AHCKMCBCX3': '', u'test-2020-07910-06_AHCKMCBCX3': '', u'pcs-2020-05298-01_AHCKMCBCX3': '', u'test-2020-07885-06_AHCKMCBCX3': '', u'test-2020-07888-06_AHCKMCBCX3': '', u'test-2020-07884-06_AHCKMCBCX3': '', u'test-2020-07896-06_AHCKMCBCX3': '', u'test-2020-07895-06_AHCKMCBCX3': '', u'test-2020-07894-06_AHCKMCBCX3': ''}


# NCV_data={u'test-2020-07892-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 4.0}, 'NCV_Y': {'warn': 'default', 'val': -0.54}, 'NCV_X': {'warn': 'default', 'val': 2.09}, 'NCV_21': {'warn': 'default', 'val': -0.12}, 'NCV_13': {'warn': 'default', 'val': -1.09}, 'NCV_18': {'warn': 'danger', 'val': 11.44}}, u'test-2020-07887-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 8.0}, 'NCV_Y': {'warn': 'default', 'val': -0.57}, 'NCV_X': {'warn': 'default', 'val': -0.94}, 'NCV_21': {'warn': 'default', 'val': 0.03}, 'NCV_13': {'warn': 'default', 'val': 0.61}, 'NCV_18': {'warn': 'default', 'val': -0.35}}, u'test-2020-07897-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 9.0}, 'NCV_Y': {'warn': 'default', 'val': 219.09}, 'NCV_X': {'warn': 'default', 'val': -10.79}, 'NCV_21': {'warn': 'default', 'val': -0.11}, 'NCV_13': {'warn': 'default', 'val': 0.05}, 'NCV_18': {'warn': 'default', 'val': 1.38}}, u'test-2020-07893-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 10.0}, 'NCV_Y': {'warn': 'default', 'val': 0.02}, 'NCV_X': {'warn': 'default', 'val': 0.17}, 'NCV_21': {'warn': 'default', 'val': -0.58}, 'NCV_13': {'warn': 'default', 'val': -0.84}, 'NCV_18': {'warn': 'default', 'val': 0.41}}, u'test-2020-07890-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 9.0}, 'NCV_Y': {'warn': 'default', 'val': 1.56}, 'NCV_X': {'warn': 'default', 'val': -1.64}, 'NCV_21': {'warn': 'default', 'val': -0.02}, 'NCV_13': {'warn': 'default', 'val': -1.95}, 'NCV_18': {'warn': 'default', 'val': -0.0}}, u'test-2020-07886-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 10.0}, 'NCV_Y': {'warn': 'default', 'val': -0.77}, 'NCV_X': {'warn': 'default', 'val': 0.67}, 'NCV_21': {'warn': 'default', 'val': 0.61}, 'NCV_13': {'warn': 'default', 'val': -0.32}, 'NCV_18': {'warn': 'default', 'val': 0.27}}, u'test-2020-07889-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 8.0}, 'NCV_Y': {'warn': 'default', 'val': 0.64}, 'NCV_X': {'warn': 'default', 'val': -0.33}, 'NCV_21': {'warn': 'default', 'val': 0.55}, 'NCV_13': {'warn': 'default', 'val': -0.52}, 'NCV_18': {'warn': 'default', 'val': -0.23}}, u'test-2020-07910-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 8.0}, 'NCV_Y': {'warn': 'default', 'val': 0.49}, 'NCV_X': {'warn': 'default', 'val': 0.47}, 'NCV_21': {'warn': 'default', 'val': -0.58}, 'NCV_13': {'warn': 'default', 'val': -0.23}, 'NCV_18': {'warn': 'default', 'val': 0.95}}, u'pcs-2020-05298-01_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 8.0}, 'NCV_Y': {'warn': 'default', 'val': 64.46}, 'NCV_X': {'warn': 'default', 'val': -3.78}, 'NCV_21': {'warn': 'default', 'val': 0.7}, 'NCV_13': {'warn': 'default', 'val': -0.89}, 'NCV_18': {'warn': 'default', 'val': 0.46}}, u'test-2020-07885-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 9.0}, 'NCV_Y': {'warn': 'default', 'val': 2.02}, 'NCV_X': {'warn': 'default', 'val': 1.4}, 'NCV_21': {'warn': 'default', 'val': 0.61}, 'NCV_13': {'warn': 'default', 'val': 0.11}, 'NCV_18': {'warn': 'default', 'val': 0.59}}, u'test-2020-07888-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 12.0}, 'NCV_Y': {'warn': 'default', 'val': 169.68}, 'NCV_X': {'warn': 'default', 'val': -10.82}, 'NCV_21': {'warn': 'default', 'val': 0.04}, 'NCV_13': {'warn': 'default', 'val': -0.5}, 'NCV_18': {'warn': 'default', 'val': -0.42}}, u'test-2020-07884-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 7.0}, 'NCV_Y': {'warn': 'default', 'val': 116.61}, 'NCV_X': {'warn': 'default', 'val': -7.22}, 'NCV_21': {'warn': 'default', 'val': 0.11}, 'NCV_13': {'warn': 'default', 'val': 0.78}, 'NCV_18': {'warn': 'default', 'val': 0.75}}, u'test-2020-07896-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 4.0}, 'NCV_Y': {'warn': 'default', 'val': 78.66}, 'NCV_X': {'warn': 'default', 'val': -3.38}, 'NCV_21': {'warn': 'default', 'val': 0.58}, 'NCV_13': {'warn': 'default', 'val': -1.36}, 'NCV_18': {'warn': 'default', 'val': -0.34}}, u'test-2020-07895-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 9.0}, 'NCV_Y': {'warn': 'default', 'val': -0.56}, 'NCV_X': {'warn': 'default', 'val': -1.12}, 'NCV_21': {'warn': 'default', 'val': -0.76}, 'NCV_13': {'warn': 'default', 'val': -0.06}, 'NCV_18': {'warn': 'default', 'val': -0.63}}, u'test-2020-07894-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 8.0}, 'NCV_Y': {'warn': 'default', 'val': 114.35}, 'NCV_X': {'warn': 'default', 'val': -8.11}, 'NCV_21': {'warn': 'default', 'val': 0.0}, 'NCV_13': {'warn': 'default', 'val': 0.25}, 'NCV_18': {'warn': 'default', 'val': -1.57}}}
