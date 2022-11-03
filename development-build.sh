#!/bin/bash
python setup.py sdist bdist_wheel
python -m twine upload --repository testpypi dist/* --verbose
mv dist/*.whl .
echo "Done. You can now upload the wheel to GitHub."
read -p "Press Enter to delete the wheel. " </dev/tty
rm -rf dist/ build/ *.egg-info/ pheonix/__pycache__ ppm/__pycache__ __pycache__ *.whl