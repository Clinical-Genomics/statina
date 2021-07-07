STATUS_CLASSES = {
    "Suspected": "warning",
    "False Positive": "success",
    "Verified": "danger",
    "Probable": "warning",
    "False Negative": "danger",
    "Other": "warning",
    "Failed": "danger",
}
CHROM_ABNORM = ["13", "18", "21", "X0", "XXX", "XXY", "XYY"]
TRIS_CHROM_ABNORM = ["13", "18", "21"]
SEX_CHROM_ABNORM = ["X0", "XXX", "XXY", "XYY"]
STATUS_COLORS = {
    "Suspected": "#DBA901",
    "Probable": "#0000FF",
    "False Negative": "#ff6699",
    "Verified": "#00CC00",
    "Other": "#603116",
    "False Positive": "#E74C3C",
}

TRISOMI_TRESHOLDS = {
    "soft_max": {"Zscore": 2.5, "color": "orange", "text": "Warning threshold = 2.5"},
    "soft_min": {"Zscore": -4, "color": "orange", "text": "Warning threshold = -4"},
    "hard_max": {"Zscore": 4, "color": "red", "text": "Threshold = 4"},
    "hard_min": {"Zscore": -5, "color": "red", "text": "Threshold = -5"},
}

FF_TRESHOLDS = {
    "fetal_fraction_preface": 7,
    "fetal_fraction_y_max": 3,
    "fetal_fraction_y_min": 0.6,
}

SEX_THRESHOLDS = {
    "y_min": -1,
    "y_max": 20,
    "xx_lower": -1,
    "xx_upper": 3.4,
    "xy_lowest": 0.6,
    "k_upper": 1.51,
    "k_lower": 1.49,
}
