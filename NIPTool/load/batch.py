import logging
from typing import Dict, List, Optional

from NIPTool.adapter import NiptAdapter

from NIPTool.parse.batch import pars_segmental_calls
from NIPTool.models.database import Batch, Sample
from NIPTool.models.server.load import BatchRequestBody

LOG = logging.getLogger(__name__)


def load_batch(adapter: NiptAdapter, batch: Batch, batch_files: BatchRequestBody) -> None:
    """Function to load data from fluffy result file."""

    batch_dict = batch.dict(exclude_none=True)
    batch_dict["_id"] = batch_dict["SampleProject"]
    batch_dict["segmental_calls"] = batch_files.segmental_calls
    batch_dict["multiqc_report"] = batch_files.multiqc_report
    batch_dict["result_file"] = batch_files.result_file
    adapter.add_or_update_document(document_news=batch_dict,
                                   collection=adapter.batch_collection)


def load_samples(
        adapter: NiptAdapter, samples: List[Sample], segmental_calls: Optional[str]
) -> None:
    """Function to load data from fluffy result file."""

    segmental_calls: Dict[str, str] = pars_segmental_calls(segmental_calls_path=segmental_calls)
    for sample in samples:
        sample_dict: dict = sample.dict(exclude_none=True)
        sample_id = sample_dict["SampleID"]
        sample_dict["_id"] = sample_id
        sample_dict["segmental_calls"] = segmental_calls.get(sample_id)
        adapter.add_or_update_document(
            document_news=sample_dict, collection=adapter.sample_collection
        )
