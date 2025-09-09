# -- coding: utf-8 --
# @Time : 2024/6/6 11:10
# @Author : PinBar
# @File : setup.py
import os
import shutil
from setuptools import setup, find_packages


def clean_pyc_and_cache():
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'))


def parse_requirements(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # 忽略空行和注释
        requirements = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    return requirements


clean_pyc_and_cache()

setup(
    name="fastapi_build",
    version="1.0.4",
    packages=find_packages(),
    url="https://github.com/tosmart01/fastapi-build",
    include_package_data=True,
    exclude_package_data={'': ['*.pyc', '__pycache__/*', '*.db']},
    install_requires=parse_requirements('requirements.txt'),
    entry_points={
        "console_scripts": [
            "fbuild=fastapi_build.scripts.cli:cli",
        ],
    },
    package_data={
        "": ["*.md", "*.txt", "docker_build.sh", "Dockerfile", ".gitignores", "alembic.ini", 'script.py.mako',
             "scripts/example_file"
             ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
