# -- coding: utf-8 --
# @Time : 2024/6/6 14:26
# @Author : PinBar
# @File : startapp.py
from pathlib import Path

import click

from . import StyledCommand
from .remove_header import remove_header
from .copy_exclude import copy_tree


@click.command(cls=StyledCommand,help=click.style("To create the app, you need to navigate to the "
                     "you_project/src directory, and then run it.", ))
@click.argument('app_name')
def main(app_name: str):
    target_dir = Path.cwd() / 'api'
    package_dir = Path(__file__).parent.resolve()
    api_dir = target_dir

    if not api_dir.exists():
        click.secho('Error:', fg='red', bold=True)
        click.echo('You need to navigate to the you_project/src directory', err=True)
        click.secho('and ensure you have create a project first before creating an app.', fg='red', err=True)
        click.secho('\nTo create a project, follow these steps:', fg='yellow', bold=True)
        click.secho('1. Create a new project:', fg='yellow')
        click.secho('   fbuild startproject your_project_name', fg='yellow')
        click.secho('2. Change to the project directory:', fg='yellow')
        click.secho('   cd your_project_name/src', fg='yellow')
        click.secho('3. Add an app (optional):', fg='yellow')
        click.secho('   fbuild startapp app_name', fg='yellow')
        return

    try:
        copy_tree(package_dir / 'example_file/init_app', api_dir / app_name)
    except FileExistsError:
        click.secho(f'Error: App {app_name} already exists in directory {api_dir}.', fg='red', err=True)
        return

    with open(Path(api_dir / app_name / '__init__.py'), 'w') as fp:
        fp.write(f"APP_NAME = '{app_name}'")

    remove_header(api_dir / app_name)
    click.secho(
        f"Successfully created app {click.style(app_name, fg='green')}, app dir: {click.style(str(api_dir / app_name), fg='blue')}, Enjoy it...",
        fg='green')


if __name__ == '__main__':
    main()
