from typing import Literal

import pymongo

SCOPES = {
    "unconfirmed": ["unconfirmed"],
    "inactive": [
        "unconfirmed",
        "inactive",
    ],
    "R": ["unconfirmed", "inactive", "R"],
    "RW": ["unconfirmed", "inactive", "R", "RW"],
    "admin": ["unconfirmed", "inactive", "R", "RW", "admin"],
}


sort_table = {"ascending": pymongo.ASCENDING, "descending": pymongo.DESCENDING}
sample_status_options = Literal[
    "Normal",
    "False Positive",
    "Suspected",
    "Verified",
    "Probable",
    "False Negative",
    "Other",
    "Failed",
]

sample_sort_keys = Literal[
    "sample_id",
    "batch_id",
    "Zscore_13",
    "Zscore_18",
    "Zscore_21",
    "Zscore_X",
    "FF_Formatted",
    "CNVSegment",
    "FFY",
    "FFX",
    "comment",
    "QCFlag",
]
