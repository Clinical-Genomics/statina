CHROM_ABNORM = ["13", "18", "21", "X0", "XXX", "XXY", "XYY"]
TRIS_CHROM_ABNORM = ["13", "18", "21"]
SEX_CHROM_ABNORM = ["X0", "XXX", "XXY", "XYY"]

TRISOMI_TRESHOLDS = {
    "soft_max": {"Zscore": 3, "color": "orange", "text": "Warning threshold = 3"},
    "hard_max": {"Zscore": 4, "color": "red", "text": "Threshold = 4"},
    "hard_min": {"Zscore": -8, "color": "red", "text": "Threshold = -8"},
}

FF_TRESHOLDS = {
    "fetal_fraction_preface": 4,
    "fetal_fraction_y_for_trisomy": 4,
    "fetal_fraction_y_max": 3,
    "fetal_fraction_y_min": 0.6,
    "fetal_fraction_XXX": -1,
    "fetal_fraction_X0": 3.4,
    "y_axis_min": -1,
    "y_axis_max": 20,
    "k_upper": 0.9809,
    "k_lower": 0.9799,
    "m_lower": -4.3987,
    "m_upper": 6.5958,
}
