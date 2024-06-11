# -- coding: utf-8 --
# @Time : 2024/6/6 14:26
# @Author : PinBar
# @File : startapp.py
from pathlib import Path

import click

from .remove_header import remove_header
from .copy_exclude import copy_tree


@click.command(
    help="To create the app, you need to navigate to the you_project/src directory, and then run it.")
@click.argument('app_name')
def main(app_name: str):
    target_dir = Path.cwd() / 'api'
    package_dir = Path(__file__).parent.resolve()
    api_dir = target_dir
    if not api_dir.exists():
        click.echo('Error: You need to navigate to the you_project/src directory', err=True)
        click.echo('and ensure you have create a project first before creating an app.', err=True)
        click.echo('\nTo create a project, follow these steps:')
        click.echo('1. Create a new project:')
        click.echo('   fbuild startproject your_project_name')
        click.echo('2. Change to the project directory:')
        click.echo('   cd your_project_name/src')
        click.echo('3. Add a app (optional):')
        click.echo('   fbuild startapp app_name')
        return
    copy_tree(package_dir / 'example_file/init_app', api_dir / app_name)
    with open(Path(api_dir / app_name / '__init__.py'), 'w') as fp:
        fp.write(f"APP_NAME = '{app_name}'")
    remove_header(api_dir / app_name)
    print(f"Successfully created app {app_name}, app dir: {api_dir / app_name}, Enjoy it...")


if __name__ == '__main__':
    main()
