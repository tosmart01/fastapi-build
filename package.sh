rm -rf build dist fastapi_build.egg-info/
python setup.py sdist bdist_wheel
twine upload dist/*
