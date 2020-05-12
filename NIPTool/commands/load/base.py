#!/usr/bin/env python
import logging

import click

from mongo_adapter import get_client
from NIPTool.adapter import NiptAdapter

LOG = logging.getLogger(__name__)

# commands
from NIPTool.commands.load.batch import batch as batch_command

# Get version and doc decorator
from NIPTool import __version__
from NIPTool.tools.cli_utils import add_doc as doc

@click.group()
@click.version_option(version=__version__)
def load():
    """Main entry point of load commands"""
    pass


load.add_command(batch_command)


