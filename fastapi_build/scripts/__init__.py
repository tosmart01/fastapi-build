# -- coding: utf-8 --
# @Time : 2024/6/6 11:19
# @Author : PinBar
# @File : __init__.py.py
import click


class StyledCommand(click.Command):
    def format_options(self, ctx, formatter):
        """Customize the options formatting to include styles."""
        options = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                # 自动为未上色的帮助文本添加绿色
                option_name, help_text = rv
                # help_text = click.style(help_text, fg="white")
                styled_option = click.style(option_name, fg="cyan")  # 选项名称的样式
                options.append((styled_option, help_text))
        if options:
            with formatter.section('Options'):
                formatter.write_dl(options)
