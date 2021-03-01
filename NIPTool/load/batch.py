import logging
from typing import Dict, List, Optional

from NIPTool.adapter import NiptAdapter

from NIPTool.parse.batch import pars_segmental_calls
from NIPTool.schemas.batch import Batch
from NIPTool.schemas.sample import Sample

LOG = logging.getLogger(__name__)


def load_batch(adapter: NiptAdapter, batch_id: str, batch: Batch) -> None:
    """Function to load data from fluffy result file."""
    mongo_batch = batch.dict(exclude_none=True)
    mongo_batch["_id"] = batch_id
    adapter.add_or_update_document(mongo_batch, adapter.batch_collection)


def load_samples(adapter, samples: List[Sample], segmental_calls: Optional[str]) -> None:
    """Function to load data from fluffy result file."""

    segmental_calls: Dict[str, str] = pars_segmental_calls(segmental_calls_path=segmental_calls)
    for sample in samples:
        mongo_sample: dict = sample.dict(exclude_none=True)
        sample_id = mongo_sample.pop("SampleID")
        segmental_calls_path = segmental_calls.get(sample_id)
        mongo_sample["_id"] = sample_id
        if segmental_calls_path:
            mongo_sample["segmental_calls"] = segmental_calls

        adapter.add_or_update_document(mongo_sample, adapter.sample_collection)
