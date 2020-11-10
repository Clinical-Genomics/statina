import logging
import click
from NIPTool.load.batch import load_one_batch
from flask.cli import with_appcontext, current_app
from datetime import date, timedelta
from NIPTool.exeptions import NIPToolError


LOG = logging.getLogger(__name__)


@click.command("batch", short_help="load batch into db.")
@click.option("-b", "--batch-path", help="path to batch load config")
@with_appcontext
def batch(batch_path):
    """Read and load lims data for one sample, all samples or the most recently updated samples."""

    try:
        load_one_batch(current_app.adapter, batch_path)
    except NIPToolError as e:
        LOG.error(e.message)
        raise click.Abort()
