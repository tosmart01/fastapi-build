# -- coding: utf-8 --
# @Time : 2024/6/6 15:32
# @Author : PinBar
# @File : cli.py
import click
from . import startproject, startapp, add_plugin


@click.group()
def cli():
    pass


cli.add_command(startproject.main, name="startproject")
cli.add_command(startapp.main, name="startapp")
cli.add_command(add_plugin.main, name="add_plugin")

if __name__ == "__main__":
    cli()
