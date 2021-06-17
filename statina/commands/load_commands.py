import logging
from pathlib import Path
from typing import List

import click
from pymongo import MongoClient

from statina.adapter import StatinaAdapter
from statina.config import settings
from statina.crud import find, insert
from statina.exeptions import InsertError
from statina.models.database import Batch, DataBaseSample
from statina.models.server.load import BatchRequestBody, UserRequestBody
from statina.parse.batch import get_batch, get_samples

LOG = logging.getLogger(__name__)


@click.group(name="load")
@click.pass_obj
def load_commands(context: dict):
    client = MongoClient(settings.db_uri)
    context["adapter"] = StatinaAdapter(client, db_name=settings.db_name)
    LOG.info("Connected to %s", settings.db_name)


@load_commands.command(name="batch")
@click.option("--result-file", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--multiqc-report", type=click.Path(dir_okay=False))
@click.option("--segmental-calls", type=click.Path(dir_okay=False))
@click.pass_obj
def load_batch(
    context: dict, result_file: click.Path, multiqc_report: click.Path, segmental_calls: click.Path
):
    """Load fluffy result into database"""
    batch_files: BatchRequestBody = BatchRequestBody(
        result_file=str(result_file),
        multiqc_report=str(multiqc_report),
        segmental_calls=str(segmental_calls),
    )
    adapter: StatinaAdapter = context["adapter"]
    nipt_results = Path(str(result_file))
    samples: List[DataBaseSample] = get_samples(nipt_results)
    batch: Batch = get_batch(nipt_results)
    if find.batch(adapter=adapter, batch_id=batch.batch_id):
        return "batch already in database"
    insert.insert_batch(adapter=adapter, batch=batch, batch_files=batch_files)
    insert.insert_samples(
        adapter=adapter, samples=samples, segmental_calls=batch_files.segmental_calls
    )


@load_commands.command(name="user")
@click.option("--email", required=True)
@click.option("--user-name", required=True)
@click.option("--role", type=click.Choice(["RW", "R", "admin"]), default="RW", show_default=True)
@click.pass_obj
def load_user(context: dict, email: str, user_name: str, role: str):
    """Add a user to the database"""
    user: UserRequestBody = UserRequestBody(email=email, username=user_name, role=role)
    adapter: StatinaAdapter = context["adapter"]

    try:
        insert.insert_user(adapter=adapter, user=user)
    except InsertError as err:
        LOG.warning(err)
        raise click.Abort
