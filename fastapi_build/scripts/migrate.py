# -- coding: utf-8 --
# @Time : 2024/6/11 14:15
# @Author : PinBar
# @File : migrate.py
import click
import subprocess
import sys
from pathlib import Path


from . import StyledCommand

ALEMBIC_NOT_INSTALLED_MESSAGE = click.style("""
Alembic is not installed. Please install it using the following command:
    pip install alembic
""", fg='yellow', bold=True)


def check_alembic_directory():
    alembic_dir = Path.cwd() / "alembic"
    if not alembic_dir.exists():
        click.secho('Error:', fg='red', bold=True)
        click.echo('\nAlembic directory not found. \n')
        click.echo('Please navigate to your_project/src directory and ensure you have added the migrate plugin.\n')
        click.echo('You can install the migrate plugin using the following command:')
        click.secho('    fbuild add_plugin migrate', fg='yellow')
        sys.exit(1)
    return alembic_dir


def check_alembic_installed():
    try:
        import alembic  # noqa: F401
    except ImportError:
        click.secho(ALEMBIC_NOT_INSTALLED_MESSAGE, err=True)
        sys.exit(1)


def run_alembic_command(command: list[str]):
    check_alembic_installed()
    alembic_dir = check_alembic_directory()
    result = subprocess.run(["alembic"] + command)
    if result.returncode != 0:
        click.secho(f"Error: Alembic command {' '.join(command)} failed.", fg='red', err=True)
        sys.exit(result.returncode)


@click.command(cls=StyledCommand,help=click.style("Run the alembic revision, like Django python manage.py makemigrations", ))
@click.option("-m", default="description", help=click.style("The description of the makemigrations",))
def makemigrations(m: str):
    click.echo(click.style(f"Generating migration with description: {m}", fg='yellow'))
    run_alembic_command(["revision", "--autogenerate", "-m", f"'{m}'"])
    click.secho(f"Successfully generated new migration revision with description '{m}'.", fg='green')


@click.command(cls=StyledCommand,help=click.style("Run the alembic history, like Django python manage.py showmigrations",))
def showmigrations():
    click.echo(click.style("Retrieving migration history...", fg='yellow'))
    run_alembic_command(["history"])


@click.command(cls=StyledCommand,help=click.style("Run the alembic upgrade head, like Django python manage.py migrate" ))
def migrate():
    click.echo(click.style("Upgrading database to the latest revision...", fg='yellow'))
    run_alembic_command(["upgrade", "head"])
    click.secho("Successfully upgraded the database to the latest revision.", fg='green')

