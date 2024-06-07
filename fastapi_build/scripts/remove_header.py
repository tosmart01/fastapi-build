# -- coding: utf-8 --
# @Time : 2024/6/6 15:18
# @Author : PinBar
# @File : remove_header.py
from pathlib import Path
from glob import glob

def remove_header(path):
    filelist = glob(str(Path(path) / '**' / '*.py'), recursive=True)
    for filepath in filelist:
        with open(filepath, encoding='utf-8') as fp:
            content = fp.readlines()
            if len(content) >= 4:
                prefix = ''.join([i[0] for i in content[:6]])
                if prefix[:4] == '####':
                    with open(filepath, 'w',encoding='utf-8') as fp:
                        fp.write(''.join(content[4:]))




