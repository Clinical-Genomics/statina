from typing import Iterable

import logging

from statina.adapter import StatinaAdapter
from statina.crud.find.find import batch_samples


LOG = logging.getLogger(__name__)


def delete_batch_document(adapter: StatinaAdapter, batch_id: str):
    adapter.batch_collection.delete_one({"batch_id": batch_id})
    LOG.info(f"Deleting batch {batch_id}")


def delete_sample_document(adapter: StatinaAdapter, sample_id: str):
    adapter.sample_collection.delete_one({"sample_id": sample_id})
    LOG.info(f"Deleting sample {sample_id}")


def delete_batch(adapter: StatinaAdapter, batch_id: str):
    samples = batch_samples(adapter=adapter, batch_id=batch_id)
    for sample in samples:
        delete_sample_document(adapter=adapter, sample_id=sample.sample_id)
    delete_batch_document(adapter=adapter, batch_id=batch_id)


def delete_batches(adapter: StatinaAdapter, batches: Iterable[str]):
    for batch_id in batches:
        delete_batch(adapter=adapter, batch_id=batch_id)
