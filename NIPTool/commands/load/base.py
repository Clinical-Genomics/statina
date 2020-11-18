#!/usr/bin/env python
import click

# commands
from NIPTool.commands.load.user import user as load_user_cmd

# Get version
from NIPTool import __version__


@click.group()
@click.version_option(version=__version__)
def load():
    """Main entry point of load commands"""
    pass


load.add_command(load_user_cmd)
