# -- coding: utf-8 --
# @Time : 2024/6/11 14:15
# @Author : PinBar
# @File : migrate.py
import subprocess
import sys
from pathlib import Path

import click

ALEMBIC_NOT_INSTALLED_MESSAGE = """
Alembic is not installed. Please install it using the following command:
    pip install alembic
"""


def check_alembic_directory():
    alembic_dir = Path.cwd() / "alembic"
    if not alembic_dir.exists():
        click.echo(
            "Alembic directory not found. \n\n"
            "Please navigate to your_project/src directory and ensure you have added the migrate plugin.\n\n"
            " You can install the migrate plugin using the following command:")
        click.echo("    fbuild add_plugin migrate")
        sys.exit(1)
    return alembic_dir


def check_alembic_installed():
    try:
        import alembic  # noqa: F401
    except ImportError:
        print(ALEMBIC_NOT_INSTALLED_MESSAGE)
        sys.exit(1)


def run_alembic_command(command: list[str]):
    check_alembic_installed()
    check_alembic_directory()
    result = subprocess.run(["alembic"] + command)
    if result.returncode != 0:
        print(f"Error: Alembic command {' '.join(command)} failed.")
        sys.exit(result.returncode)


@click.command(help="Run the alembic revision, like Django python manage.py makemigrations")
@click.option("-m", default="description", help="The description of the makemigrations")
def makemigrations(m: str):
    run_alembic_command(["revision", "--autogenerate", "-m", f"'{m}'"])


@click.command(help="Run the alembic history, like Django python manage.py showmigrations")
def showmigrations():
    run_alembic_command(["history"])


@click.command(help="Run the alembic upgrade head, like Django python manage.py migrate")
def migrate():
    run_alembic_command(["upgrade", "head"])
