#!/bin/bash
python setup.py sdist bdist_wheel
python -m twine upload dist/* --verbose
rm -rf dist/ build/ pheonix_ws.egg-info/ pheonix/__pycache__ ppm/__pycache__
