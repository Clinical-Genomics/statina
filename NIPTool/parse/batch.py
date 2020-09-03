import logging
import pandas as pd
import glob
from NIPTool.exeptions import MissingResultsError, FileValidationError
from NIPTool.models.nipt_results import nipt_results_schema

LOG = logging.getLogger(__name__)


def parse_batch_file(nipt_results_path: dict) -> list:
    if not glob.glob(nipt_results_path):
        raise MissingResultsError("Results file missing.")

    nipt_results = glob.glob(nipt_results_path)[0]
    df = pd.read_csv(nipt_results, na_filter=False)

    errors = nipt_results_schema.validate(df)

    for err in errors:
        LOG.warning(err)

    if errors:
        raise FileValidationError("Invalid file content.")

    result = df.to_dict(orient="records")
    return result
