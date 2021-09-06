"""
Module with CLI commands for Statina

The CLI is intended for development/testing purpose only. To run in a production setting please refer to documentation
for suggestions how.

"""
import logging

import click
import pkg_resources
import uvicorn

# Get version and doc decorator
from statina import __version__
from statina.commands.load_commands import load_commands
from statina.config import settings

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG = logging.getLogger(__name__)

ENV_FILE = pkg_resources.resource_filename("statina", ".env")


@click.version_option(__version__)
@click.group()
@click.pass_context
def cli(context: click.Context):
    """Main entry point"""
    logging.basicConfig(level=logging.INFO)
    context.obj = {}


@cli.command(name="serve")
@click.option(
    "--api", default="external", type=click.Choice(["external", "internal"]), show_default=True
)
@click.option("--version", default="v1", type=click.Choice(["v1", "v2"]), show_default=True)
@click.option("--reload", is_flag=True)
def serve_command(reload: bool, api: str, version: str):
    """Serve the Statina app for testing purpose.

    This command will serve the user interface (external) as default
    """
    app = f"statina.main:{api}_app"
    LOG.info("Running %s api on host:%s and port:%s", api, settings.host, settings.port)
    uvicorn.run(app=app, host=settings.host, port=settings.port, reload=reload)


cli.add_command(load_commands)
