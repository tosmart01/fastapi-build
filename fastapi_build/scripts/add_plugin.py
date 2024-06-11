# -- coding: utf-8 --
# @Time : 2024/6/6 15:04
# @Author : PinBar
# @File : add_plugin.py
import shutil
from pathlib import Path

import click

from .remove_header import remove_header
from .copy_exclude import copy_tree


def copy_list(source: Path, target: Path):
    for filepath in (source).glob('*.py'):
        if filepath.name != 'user.py' and not filepath.name.endswith('pyc'):
            shutil.copy(filepath, target / filepath.name)


def copy_dao(package_dir: Path, target_dir: Path):
    copy_tree(package_dir / 'dao', target_dir / 'dao')
    (target_dir / 'dao' / 'user_dao.py').unlink(missing_ok=True)


@click.command(help='Register a plugin for the application.\n\n'
                    'Available plugins:\n\n'
                    '  - db: all database support\n\n'
                    '  - db[mysql]: MySQL database support\n\n'
                    '  - db[redis]: Redis database support\n\n'
                    '  - db[es]: Elasticsearch support\n\n'
                    '  - migrate: migrate support like Django migrate\n\n'
                    '  - celery: Celery task queue support\n\n'
                    '  - all: all plugin \n'
               )
@click.argument('plugin_name',
                type=click.Choice(['db', 'db[mysql]', 'db[redis]', 'db[es]', 'migrate', 'celery', 'all'], ))
def main(plugin_name: str):
    target_dir = Path.cwd()
    if not (target_dir / 'api').exists():
        click.echo('Error: You need to navigate to the you_project/src directory', err=True)
        click.echo("and ensure you have create a project first before register plugin.", err=True)
        click.echo('\nTo create a project, follow these steps:')
        click.echo('1. Create a new project:')
        click.echo('   fbuild startproject your_project_name')
        click.echo('2. Change to the project directory:')
        click.echo('   cd your_project_name')
        click.echo('3. Add a plugin (optional):')
        click.echo('   fbuild add_plugin plugin_name')
        return
    package_dir = Path(__file__).parent.parent.resolve()
    ALL = plugin_name == 'all'
    if plugin_name.startswith('db') or ALL:
        (target_dir / 'db' / 'backends').mkdir(parents=True, exist_ok=True)
        (target_dir / 'db' / 'backends' / '__init__.py').touch(exist_ok=True)
    if plugin_name == 'db' or ALL:
        (target_dir / 'db' / 'models').mkdir(parents=True, exist_ok=True)
        copy_list(package_dir / 'db' / 'backends', target_dir / 'db' / 'backends')
        copy_list(package_dir / 'db' / 'models', target_dir / 'db' / 'models')
        copy_dao(package_dir, target_dir)
        remove_header(target_dir / 'db')
        remove_header(target_dir / 'dao')
    if plugin_name == 'db[mysql]' or ALL:
        (target_dir / 'db' / 'models').mkdir(parents=True, exist_ok=True)
        shutil.copy(package_dir / 'db' / 'backends' / 'mysql.py', target_dir / 'db' / 'backends' / 'mysql.py')
        copy_list(package_dir / 'db' / 'models', target_dir / 'db' / 'models')
        copy_dao(package_dir, target_dir)
        remove_header(target_dir / 'db')
        remove_header(target_dir / 'dao')
    if plugin_name == 'db[redis]' or ALL:
        shutil.copy(package_dir / 'db' / 'backends' / 'redis_client.py',
                    target_dir / 'db' / 'backends' / 'redis_client.py')
        remove_header(target_dir / 'db' / 'backends')
    if plugin_name == 'db[es]' or ALL:
        shutil.copy(package_dir / 'db' / 'backends' / 'es.py', target_dir / 'db' / 'backends' / 'es.py')
        remove_header(target_dir / 'db' / 'backends')
    if plugin_name == 'celery' or ALL:
        copy_tree(package_dir / 'celery_task', target_dir / 'celery_task')
        remove_header(target_dir / 'celery_task')
    if plugin_name == 'migrate' or ALL:
        (target_dir / 'alembic').mkdir(parents=True, exist_ok=True)
        (target_dir / 'alembic' / 'versions').mkdir(parents=True, exist_ok=True)
        shutil.copy(package_dir / 'scripts' / 'example_file/script.py.mako', target_dir / 'alembic' / 'script.py.mako')
        shutil.copy(package_dir / 'scripts' / 'example_file/alembic.ini', target_dir / 'alembic.ini')
        shutil.copy(package_dir / 'scripts' / 'example_file/alembic_env.py', target_dir / 'alembic' / 'env.py')

    print(f"Successfully install plugin {plugin_name}")


if __name__ == '__main__':
    main()
