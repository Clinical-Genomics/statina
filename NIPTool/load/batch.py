import logging
from typing import Dict, List, Optional

from NIPTool.adapter import NiptAdapter

from NIPTool.parse.batch import pars_segmental_calls
from NIPTool.schemas.db_models.batch import BatchModel
from NIPTool.schemas.db_models.sample import SampleModel
from NIPTool.schemas.server import BatchLoadModel

LOG = logging.getLogger(__name__)


def load_batch(adapter: NiptAdapter, batch: BatchModel, batch_files: BatchLoadModel) -> None:
    """Function to load data from fluffy result file."""

    mongo_batch = batch.dict(exclude_none=True)
    batch_id = mongo_batch.pop("SampleProject")
    mongo_batch["_id"] = batch_id
    mongo_batch["segmental_calls"] = batch_files.segmental_calls
    mongo_batch["multiqc_report"] = batch_files.multiqc_report
    mongo_batch["result_file"] = batch_files.result_file
    adapter.add_or_update_document(document_news=mongo_batch, collection=adapter.batch_collection)


def load_samples(
    adapter: NiptAdapter, samples: List[SampleModel], segmental_calls: Optional[str]
) -> None:
    """Function to load data from fluffy result file."""

    segmental_calls: Dict[str, str] = pars_segmental_calls(segmental_calls_path=segmental_calls)
    for sample in samples:
        mongo_sample: dict = sample.dict(exclude_none=True)
        sample_id = mongo_sample.pop("SampleID")
        segmental_calls_path = segmental_calls.get(sample_id)
        mongo_sample["_id"] = sample_id
        if segmental_calls_path:
            mongo_sample["segmental_calls"] = segmental_calls_path

        adapter.add_or_update_document(
            document_news=mongo_sample, collection=adapter.sample_collection
        )
