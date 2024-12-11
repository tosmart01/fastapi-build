# -- coding: utf-8 --
# @Time : 2024/6/6 15:04
# @Author : PinBar
# @File : add_plugin.py
import shutil
from pathlib import Path

from .remove_header import remove_header
from .copy_exclude import copy_tree


def copy_list(source: Path, target: Path):
    for filepath in (source).glob('*.py'):
        if filepath.name != 'user.py' and not filepath.name.endswith('pyc'):
            shutil.copy(filepath, target / filepath.name)


def copy_dao(package_dir: Path, target_dir: Path):
    copy_tree(package_dir / 'dao', target_dir / 'dao')
    (target_dir / 'dao' / 'user_dao.py').unlink(missing_ok=True)


def add_plugin(plugin_name, target_dir: Path, package_dir: Path):
    ALL = plugin_name == 'all'
    if plugin_name.startswith('db') or ALL:
        (target_dir / 'db').mkdir(parents=True, exist_ok=True)
        (target_dir / 'db' / '__init__.py').touch(exist_ok=True)
    if plugin_name == 'db' or ALL:
        (target_dir / 'models').mkdir(parents=True, exist_ok=True)
        copy_list(package_dir / 'db', target_dir / 'db')
        copy_list(package_dir / 'models', target_dir / 'models')
        copy_dao(package_dir, target_dir)
        remove_header(target_dir / 'db')
        remove_header(target_dir / 'dao')
    if plugin_name == 'db[database]' or ALL:
        (target_dir / 'models').mkdir(parents=True, exist_ok=True)
        shutil.copy(package_dir / 'db' / 'database.py', target_dir / 'db' / 'database.py')
        copy_list(package_dir / 'models', target_dir / 'models')
        copy_dao(package_dir, target_dir)
        remove_header(target_dir / 'db')
        remove_header(target_dir / 'dao')
    if plugin_name == 'db[redis]' or ALL:
        shutil.copy(package_dir / 'db' / 'redis_client.py',
                    target_dir / 'db' / 'redis_client.py')
        remove_header(target_dir / 'db')
    if plugin_name == 'db[es]' or ALL:
        shutil.copy(package_dir / 'db' / 'es.py', target_dir / 'db' / 'es.py')
        remove_header(target_dir / 'db' )
    if plugin_name == 'celery' or ALL:
        copy_tree(package_dir / 'celery_task', target_dir / 'celery_task')
        remove_header(target_dir / 'celery_task')
    if plugin_name == 'migrate' or ALL:
        (target_dir / 'alembic').mkdir(parents=True, exist_ok=True)
        (target_dir / 'alembic' / 'versions').mkdir(parents=True, exist_ok=True)
        shutil.copy(package_dir / 'scripts' / 'example_file/script.py.mako', target_dir / 'alembic' / 'script.py.mako')
        shutil.copy(package_dir / 'scripts' / 'example_file/alembic.ini', target_dir / 'alembic.ini')
        shutil.copy(package_dir / 'scripts' / 'example_file/alembic_env.py', target_dir / 'alembic' / 'env.py')


import click
from pathlib import Path


@click.command(
    help=(
        click.style('Register a plugin for the application.', fg='green') + '\n\n' +
        'Available plugins:\n' +
        f'\n\n{click.style(  "  - db", fg="blue")}: all database support' +
        f'\n\n{click.style("  - db[database]", fg="blue")}: database support' +
        f'\n\n{click.style("  - db[redis]", fg="blue")}: Redis database support' +
        f'\n\n{click.style("  - db[es]", fg="blue")}: Elasticsearch support' +
        f'\n\n{click.style("  - migrate", fg="blue")}: migrate support like Django migrate' +
        f'\n\n{click.style("  - celery", fg="blue")}: Celery task queue support' +
        f'\n\n{click.style("  - all", fg="blue")}: all plugin'
    )
)
@click.argument('plugin_name',
                type=click.Choice(['db', 'db[database]', 'db[redis]', 'db[es]', 'migrate', 'celery', 'all'], ))
def main(plugin_name: str):
    target_dir = Path.cwd()
    if not (target_dir / 'api').exists():
        click.secho('Error:', fg='red', bold=True)
        click.echo('You need to navigate to the you_project/src directory', err=True)
        click.secho("and ensure you have create a project first before register plugin.", fg='red', err=True)
        click.secho('\nTo create a project, follow these steps:', fg='yellow', bold=True)
        click.secho('1. Create a new project:', fg='yellow')
        click.secho('   fbuild startproject your_project_name', fg='yellow')
        click.secho('2. Change to the project directory:', fg='yellow')
        click.secho('   cd your_project_name', fg='yellow')
        click.secho('3. Add a plugin (optional):', fg='yellow')
        click.secho('   fbuild add_plugin plugin_name', fg='yellow')
        return

    package_dir = Path(__file__).parent.parent.resolve()
    add_plugin(plugin_name, target_dir, package_dir)

    click.secho(f"Successfully installed plugin {click.style(plugin_name, fg='green', bold=True)}", fg='green')


if __name__ == '__main__':
    main()
