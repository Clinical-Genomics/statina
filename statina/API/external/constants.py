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
    "soft_max_ff": {"NCV": 2.5, "color": "orange", "text": "Warning threshold = 2.5"},
    "soft_max": {"NCV": 3, "color": "orange", "text": "Warning threshold = 3"},
    "soft_min": {"NCV": -4, "color": "orange", "text": "Warning threshold = -4"},
    "hard_max": {"NCV": 4, "color": "red", "text": "Threshold = 4"},
    "hard_min": {"NCV": -5, "color": "red", "text": "Threshold = -5"},
}

FF_TRESHOLD = 3
