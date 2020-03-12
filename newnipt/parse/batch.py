
import logging
import csv
import glob

LOG = logging.getLogger(__name__)

def parse_batch_file(flowcell_id: str, analysis_path: str) -> list:
    nipt_results_path = f"{analysis_path}*{flowcell_id}*/*NIPT_RESULTS.csv"
    if not glob.glob(nipt_results_path):
        LOG.exception('Results file missing')
        return {}

    nipt_results = glob.glob(nipt_results_path)[0]
    reader = csv.DictReader(open(nipt_results))
    return list(reader)