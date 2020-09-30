import logging
import click
from NIPTool.load.user import load_user
from flask.cli import with_appcontext, current_app
from NIPTool.exeptions import NIPToolError


LOG = logging.getLogger(__name__)


@click.command("user", short_help="load batch into db.")
@click.option("-n", "--name", help="User name")
@click.option("-r", "--role", help="User name")
@click.option("-e", "--email", help="User name")
@with_appcontext
def user(name, role, email):
    """Loading new user to db."""

    try:
        load_user(current_app.adapter, email, name, role)
    except NIPToolError as e:
        LOG.error(e.message)
        raise click.Abort()
