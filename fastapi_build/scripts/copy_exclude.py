# -- coding: utf-8 --
# @Time : 2024/6/7 11:02
# @Author : PinBar
# @File : copy.py
from pathlib import Path
import shutil
from glob import glob


def copy_tree(source: Path, target: Path):
    shutil.copytree(source, target, dirs_exist_ok=True)
    for pyc in glob(str(target / "**" / "*.pyc"), recursive=True):
        Path(pyc).unlink(missing_ok=True)
    for pyc in glob(str(target / "**" / "__pycache__"), recursive=True):
        shutil.rmtree(pyc)
