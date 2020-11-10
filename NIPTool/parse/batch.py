import logging
import pandas as pd
import glob
from typing import Optional, List

from NIPTool.exeptions import MissingResultsError, FileValidationError
from NIPTool.models.validation import (
    ints,
    floats,
    strings,
    exceptions,
)

LOG = logging.getLogger(__name__)


def form(val: Optional, function) -> Optional:
    """Returning formated value or None"""

    try:
        return function(val)
    except:
        return None


def validate(key: str, val: Optional) -> Optional:
    """Formating value according to defined models."""

    if val in exceptions:
        formated_value = None
    elif key in ints:
        formated_value = form(val, int)
    elif key in floats:
        formated_value = form(val, float)
    elif key in strings:
        formated_value = form(val, str)
    else:
        formated_value = None
    return formated_value


def parse_batch_file(nipt_results_path: str) -> List[dict]:
    """Parsing file content. Formating values. Ignoring values 
    that could not be formatted according to defined models"""

    if not glob.glob(nipt_results_path):
        raise MissingResultsError("Results file missing.")

    nipt_results = glob.glob(nipt_results_path)[0]
    df = pd.read_csv(nipt_results, na_filter=False)
    results = df.to_dict(orient="records")

    samples = []
    for sample in results:
        formated_results = {}
        for key, val in sample.items():
            formated_value = validate(key, val)
            if formated_value is None:
                LOG.info(f"invalid format of {key}.")
                continue
            formated_results[key] = formated_value
        samples.append(formated_results)

    return samples
