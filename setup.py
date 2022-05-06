import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
  name="nopm",
  version="1.0.0.1",
  description="An alternative web server and package manager",
  long_description=README,
  long_description_content_type="text/markdown",
  url="https://github.com/Froggo8311/NoJS",
  author="Froggo",
  author_email="",
  license="MIT",
  classifiers=[
    "Programming Language :: Python :: 3"
  ],
  packages=[
    "nojs",
    "nojs.nopm"
    "css_html_js_minify"
  ],
  include_package_data=True,
  install_requires=[
    "flask",
    "waitress"
  ],
  entry_points={
    "console_scripts": [
      "nojs=nojs.__main__:main"
    ]
  },
  license_files = ("LICENSE",),
  keywords=[
    "NoJS",
    "NoPM",
    "Server",
    "Package Manager",
    "HTML",
    "CSS",
    "JavaScript",
    "JS",
    "Fast"
  ]
)