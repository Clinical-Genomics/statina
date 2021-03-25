import logging
from typing import Dict, List, Optional

from NIPTool.adapter import NiptAdapter

from NIPTool.parse.batch import pars_segmental_calls
from NIPTool.models.fluffy_results import FluffyBatch, FluffySample
from NIPTool.models.database import DatabaseBatch, DatabaseSample
from NIPTool.models.server.load import BatchRequestBody

LOG = logging.getLogger(__name__)


def load_batch(adapter: NiptAdapter, fluffy_batch: FluffyBatch, batch_files: BatchRequestBody) -> None:
    """Function to load data from fluffy result file."""

    mongo_batch = fluffy_batch.dict(exclude_none=True)
    batch_id = mongo_batch.pop("SampleProject")
    database_batch = DatabaseBatch(**mongo_batch, _id=batch_id, segmental_calls=batch_files.segmental_calls,
                                   multiqc_report=batch_files.multiqc_report, result_file=batch_files.result_file)

    adapter.add_or_update_document(document_news=database_batch.dict(exclude_none=True),
                                   collection=adapter.batch_collection)


def load_samples(
        adapter: NiptAdapter, fluffy_samples: List[FluffySample], segmental_calls: Optional[str]
) -> None:
    """Function to load data from fluffy result file."""

    segmental_calls: Dict[str, str] = pars_segmental_calls(segmental_calls_path=segmental_calls)
    for sample in fluffy_samples:
        mongo_sample: dict = sample.dict(exclude_none=True)
        sample_id = mongo_sample.pop("SampleID")
        segmental_calls_path = segmental_calls.get(sample_id)
        database_sample = DatabaseSample(**mongo_sample, _id=sample_id, segmental_calls=segmental_calls_path)

        adapter.add_or_update_document(
            document_news=database_sample.dict(exclude_none=True), collection=adapter.sample_collection
        )
