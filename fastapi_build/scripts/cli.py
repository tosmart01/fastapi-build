# -- coding: utf-8 --
# @Time : 2024/6/6 15:32
# @Author : PinBar
# @File : cli.py
import click
from . import startproject, startapp, add_plugin, migrate


# 自定义帮助命令类以保持命令的注册顺序
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


# 使用自定义的 OrderedGroup
@click.group(cls=OrderedGroup, context_settings=dict(help_option_names=['-h', '--help'], max_content_width=120))
def cli():
    pass


cli.add_command(startproject.main, name="startproject")
cli.add_command(startapp.main, name="startapp")
cli.add_command(add_plugin.main, name="add_plugin")
cli.add_command(migrate.makemigrations, name="makemigrations")
cli.add_command(migrate.showmigrations, name="showmigrations")
cli.add_command(migrate.migrate, name="migrate")

if __name__ == "__main__":
    cli()
