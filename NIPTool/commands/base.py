#!/usr/bin/env python
import logging
from pathlib import Path
from typing import List

import click
import pkg_resources
import uvicorn
from dotenv import dotenv_values

# Get version and doc decorator
from NIPTool import __version__
from NIPTool.adapter import NiptAdapter
from NIPTool.config import settings
from NIPTool.crud import find
from NIPTool.crud.insert import insert_batch, insert_samples
from NIPTool.main import external_app, internal_app
from NIPTool.models.database import Batch, Sample
from NIPTool.models.server.load import BatchRequestBody
from NIPTool.parse.batch import get_batch, get_samples
from pymongo import MongoClient

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG = logging.getLogger(__name__)

ENV_FILE = pkg_resources.resource_filename("NIPTool", ".env")


@click.version_option(__version__)
@click.group()
def cli():
    """ Main entry point """
    logging.basicConfig(level=logging.INFO)


@cli.command(name="load")
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


@cli.command(name="serve")
@click.option(
    "--api", default="external", type=click.Choice(["external", "internal"]), show_default=True
)
@click.option("--reload", is_flag=True)
def serve_command(reload: bool, api: str):
    app = "NIPTool.main:external_app"
    if api == "internal":
        app = "NIPTool.main:internal_app"
    LOG.info("Running %s api on host:%s and port:%s", api, settings.host, settings.port)
    uvicorn.run(app=app, host=settings.host, port=settings.port, reload=reload)
