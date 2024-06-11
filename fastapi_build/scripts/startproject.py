# -- coding: utf-8 --
# @Time : 2024/6/6 11:44
# @Author : PinBar
# @File : startproject.py
from pathlib import Path
import shutil

import click

from .copy_exclude import copy_tree
from .remove_header import remove_header

copy_dirs = ['auth', 'common', 'config', 'core', 'exceptions', 'middleware']
filename_list = ['gunicorn_conf.py', 'server.py']


def create_build_dir(project_name: str, package_dir: Path):
    build_dir = (Path.cwd() / project_name / 'build')
    build_dir.mkdir(exist_ok=True, parents=True)
    shutil.copy(package_dir / 'example_file/docker_build.sh', build_dir / 'docker_build.sh')
    shutil.copy(package_dir / 'example_file/Dockerfile', build_dir / 'Dockerfile')


@click.command(help='Create project folder')
@click.option('--example-api', is_flag=True, help='Include an example API in the created project.',
              default=False)
@click.argument('project_name')
def main(example_api, project_name: str):
    target_dir = Path.cwd() / project_name / 'src'
    target_dir.mkdir(parents=True, exist_ok=False)
    package_dir = Path(__file__).parent.resolve()

    create_build_dir(project_name, package_dir)
    shutil.copy(package_dir / 'example_file/.gitignores', Path.cwd() / project_name / '.gitignore')
    shutil.copy(package_dir / 'example_file/requirements.txt', Path.cwd() / project_name / 'requirements.txt')
    shutil.copy(package_dir / 'example_file/README.md', Path.cwd() / project_name / 'README.md')

    base_dir = Path(__file__).parent.parent.resolve()
    for row in base_dir.iterdir():
        if row.name in copy_dirs:
            copy_tree(row, target_dir / row.name)
        if row.name in filename_list:
            shutil.copy(row, target_dir)
    (target_dir / 'api').mkdir(parents=True, exist_ok=True)
    (target_dir / 'api' / '__init__.py').touch(exist_ok=True)
    if example_api:
        copy_tree(base_dir / 'api' / 'example_api', target_dir / 'api' / 'example_api')
    remove_header(target_dir)
    click.echo(f"Successfully created project {project_name}, project dir: {target_dir.parent}, Enjoy it...")


if __name__ == '__main__':
    main()
