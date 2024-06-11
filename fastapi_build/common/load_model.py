# -- coding: utf-8 --
# @Time : 2024/5/24 15:33
# @Author : PinBar
# @File : tools.py
import sys
import pathlib
from glob import glob


def import_api_module(module_path: str):
    """
    module_path 为model所在文件夹相对路径,
    并用点代替 /, app/model > app.model
    :param module_path: 'app.model'
    :return: None
    """
    base_dir = str(pathlib.Path(__file__).resolve().parent.parent)
    path = str(pathlib.Path(base_dir, *module_path.split(".")))
    for py_path in glob(str(pathlib.Path(path, '**', '*.py')), recursive=True):
        py = (
            (".".join(py_path.split(base_dir)[1:]))
            .replace(".py", "")
            .replace("/", ".")[1:]
        )
        mod = __import__(
            py,
        )
        classes = [
            getattr(mod, x) for x in dir(mod) if isinstance(getattr(mod, x), type)
        ]
        for cls in classes:
            setattr(sys.modules[module_path], cls.__name__, cls)
