import logging
from pathlib import Path
from typing import List

import click
from NIPTool.adapter import NiptAdapter
from NIPTool.config import settings
from NIPTool.crud import find
from NIPTool.crud.insert import insert_batch, insert_samples
from NIPTool.models.database import Batch, Sample
from NIPTool.models.server.load import BatchRequestBody
from NIPTool.parse.batch import get_batch, get_samples
from pymongo import MongoClient

LOG = logging.getLogger(__name__)


@click.group(name="load")
def load_commands():
    pass


@load_commands.command(name="batch")
@click.option("--result-file", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--multiqc-report", type=click.Path(dir_okay=False))
@click.option("--segmental-calls", type=click.Path(dir_okay=False))
@click.pass_obj
def load_command(
    context: dict, result_file: click.Path, multiqc_report: click.Path, segmental_calls: click.Path
):
    """Load fluffy result into database"""
    batch_files: BatchRequestBody = BatchRequestBody(
        result_file=str(result_file),
        multiqc_report=str(multiqc_report),
        segmental_calls=str(segmental_calls),
    )
    client = MongoClient(settings.db_uri)
    adapter = NiptAdapter(client, db_name=settings.db_name)
    LOG.info("Connected to %s", settings.db_name)
    nipt_results = Path(str(result_file))
    samples: List[Sample] = get_samples(nipt_results)
    batch: Batch = get_batch(nipt_results)
    if find.batch(adapter=adapter, batch_id=batch.batch_id):
        return "batch already in database"
    insert_batch(adapter=adapter, batch=batch, batch_files=batch_files)
    insert_samples(adapter=adapter, samples=samples, segmental_calls=batch_files.segmental_calls)
