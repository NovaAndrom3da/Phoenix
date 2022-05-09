#!/bin/bash
python setup.py sdist bdist_wheel
python -m twine upload dist/* --verbose
rm -rf dist/ build/ nopm.egg-info/
