import logging
import click
from NIPTool.load.batch import load_result_file, load_concentrastions, load_project_name
from flask.cli import with_appcontext, current_app
from datetime import date, timedelta
from NIPTool.exeptions import NIPToolError
import json



LOG = logging.getLogger(__name__)


@click.command("batch", short_help="load batch into db.")
@click.option("-b", "--load-config", help="path to batch load config")
@with_appcontext
def batch(load_config: dict) -> None:
    """Read and load data for one batch.
    
    Args: load_config - dict with keys: 
        "concentrations"
        "result_file"
        "project_name"
    """

    config_data = json.loads(load_config)
    
    try:
        load_result_file(current_app.adapter, config_data["result_file"])
        load_concentrastions(current_app.adapter, config_data["concentrations"])
        load_project_name(current_app.adapter, config_data["project_name"], config_data["flowcell"])
    except NIPToolError as e:
        LOG.error(e.message)
        raise click.Abort()
