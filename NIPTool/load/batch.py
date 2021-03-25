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

    fluffy_batch_dict = fluffy_batch.dict(exclude_none=True)
    batch_id = fluffy_batch_dict.pop("SampleProject")
    database_batch = DatabaseBatch(**fluffy_batch_dict, id=batch_id, segmental_calls=batch_files.segmental_calls,
                                   multiqc_report=batch_files.multiqc_report, result_file=batch_files.result_file)
    database_batch_dict = database_batch.dict(exclude_none=True, by_alias=True)
    adapter.add_or_update_document(document_news=database_batch_dict,
                                   collection=adapter.batch_collection)


def load_samples(
        adapter: NiptAdapter, fluffy_samples: List[FluffySample], segmental_calls: Optional[str]
) -> None:
    """Function to load data from fluffy result file."""

    segmental_calls: Dict[str, str] = pars_segmental_calls(segmental_calls_path=segmental_calls)
    for fluffy_sample in fluffy_samples:
        fluffy_sample_dict: dict = fluffy_sample.dict(exclude_none=True)
        sample_id = fluffy_sample_dict.pop("SampleID")
        segmental_calls_path = segmental_calls.get(sample_id)
        database_sample = DatabaseSample(**fluffy_sample_dict, _id=sample_id, segmental_calls=segmental_calls_path)
        database_sample_dict = database_sample.dict(exclude_none=True, by_alias=True)
        adapter.add_or_update_document(
            document_news=database_sample_dict, collection=adapter.sample_collection
        )
