rm -rf build dist fastapi_build.egg-info/
python setup.py sdist bdist_wheel
pip uninstall -y fastapi-build
pip install .

