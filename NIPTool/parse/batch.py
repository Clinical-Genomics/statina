import logging
import pandas as pd
import glob

LOG = logging.getLogger(__name__)


def parse_batch_file(nipt_results_path: str) -> list:
    if not glob.glob(nipt_results_path):
        LOG.exception("Results file missing")
        return {}

    nipt_results = glob.glob(nipt_results_path)[0]
    df = pd.read_csv(nipt_results, na_filter=False)
    result = df.to_dict(orient="records")
    return result
