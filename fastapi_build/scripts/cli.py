# -- coding: utf-8 --
# @Time : 2024/6/6 15:32
# @Author : PinBar
# @File : cli.py
import click
from . import startproject, add_plugin, migrate
from .. import __version__

import click


class OrderedGroup(click.Group):
    def __init__(self, *args, **kwargs):
        self.commands = []
        super().__init__(*args, **kwargs)

    def list_commands(self, ctx):
        return self.commands

    def command(self, *args, **kwargs):
        def decorator(f):
            cmd = super(OrderedGroup, self).command(*args, **kwargs)(f)
            self.commands.append(cmd.name)
            return cmd

        return decorator

    def format_commands(self, ctx, formatter):
        # Calls the parent class's format_commands to ensure commands are listed
        rows = []
        for cmd_name in self.list_commands(ctx):
            cmd = self.get_command(ctx, cmd_name)
            # Add color to command names
            styled_name = click.style(cmd_name, fg="cyan")
            rows.append((styled_name, cmd.get_short_help_str()))
        if rows:
            with formatter.section('Commands'):
                formatter.write_dl(rows)


@click.group(cls=OrderedGroup, context_settings=dict(help_option_names=['-h', '--help'], max_content_width=120))
@click.version_option(version=__version__, prog_name=click.style('Fastapi-Build', fg='blue', bold=True))
def cli():
    """Fastapi-Build is a CLI tool to help manage FastAPI projects."""
    pass


cli.add_command(startproject.main, name="startproject")
cli.add_command(add_plugin.main, name="add_plugin")
cli.add_command(migrate.makemigrations, name="makemigrations")
cli.add_command(migrate.showmigrations, name="showmigrations")
cli.add_command(migrate.migrate, name="migrate")
