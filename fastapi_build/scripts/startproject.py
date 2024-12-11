# -- coding: utf-8 --
# @Time : 2024/6/6 11:44
# @Author : PinBar
# @File : startproject.py
from pathlib import Path
import shutil
from typing import List

import click

from . import StyledCommand
from .copy_exclude import copy_tree
from .remove_header import remove_header
from .add_plugin import add_plugin

copy_dirs = ['auth', 'common', 'config', 'core', 'exceptions', 'middleware']
filename_list = ['gunicorn_conf.py', 'server.py']


def create_build_dir(project_name: str, package_dir: Path):
    build_dir = (Path.cwd() / project_name / 'build')
    build_dir.mkdir(exist_ok=True, parents=True)
    shutil.copy(package_dir / 'example_file/docker_build.sh', build_dir / 'docker_build.sh')
    shutil.copy(package_dir / 'example_file/Dockerfile', build_dir / 'Dockerfile')


@click.command(cls=StyledCommand,help=click.style('Create project folder', ))
@click.option('--example-api', is_flag=True, help=click.style('Include an example API in the created project.'), default=False)
@click.option('--all-plugin', is_flag=True, help=click.style('Include all plugins in the created project.'), default=False)
@click.argument('project_name')
def main(example_api: bool, all_plugin: bool, project_name: str):
    target_dir = Path.cwd() / project_name / 'src'
    try:
        target_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        click.secho(f'Error: Project folder {project_name} already exists.', fg='red', err=True)
        return

    package_dir = Path(__file__).parent.resolve()

    # 创建项目目录结构
    create_build_dir(project_name, package_dir)

    # 复制初始文件
    for file in ['.gitignores', 'requirements.txt', 'README.md']:
        shutil.copy(package_dir / 'example_file' / file, Path.cwd() / project_name / file.replace('ignores', 'ignore'))

    base_dir = Path(__file__).parent.parent.resolve()


    # 复制目录和文件
    for row in base_dir.iterdir():
        if row.name in copy_dirs:
            copy_tree(row, target_dir / row.name)
        elif row.name in filename_list:
            shutil.copy(row, target_dir)

    # 创建 api 目录结构
    api_dir = target_dir / 'api'
    api_dir.mkdir(parents=True, exist_ok=True)
    (api_dir / '__init__.py').touch(exist_ok=True)

    # 添加示例 API 和插件
    if example_api:
        click.echo(click.style('Adding example API...', fg='yellow'))
        copy_tree(base_dir / 'api' / 'demo_user_api', api_dir / 'example_api')
        if not all_plugin:
            add_plugin("db[database]", target_dir, package_dir.parent)
            shutil.copyfile(base_dir / 'models' / 'user.py', target_dir / 'models' / 'user.py')

    if all_plugin:
        click.echo(click.style('Adding all plugins...', fg='yellow'))
        add_plugin("all", target_dir, package_dir.parent)
        if example_api:
            shutil.copyfile(base_dir / 'models' / 'user.py', target_dir / 'models' / 'user.py')

    remove_header(target_dir)
    click.secho(
        f"Successfully created project {click.style(project_name, fg='green', bold=True)}, project dir: {click.style(str(target_dir.parent), fg='blue')}, Enjoy it...",
        fg='green')


if __name__ == '__main__':
    main()
