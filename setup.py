import pathlib
from setuptools import setup
from pheonix import VERSION

print(f"Packaging Pheonix version {VERSION}")

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
  name="pheonix",
  version=VERSION,
  description="An alternative web server and package manager",
  long_description=README,
  long_description_content_type="text/markdown",
  url="https://github.com/Froggo8311/Pheonix",
  author="Froggo",
  # author_email="",
  license="MIT",
  classifiers=[
    "Programming Language :: Python :: 3"
  ],
  packages=[
    "pheonix",
    "ppm"
  ],
  include_package_data=True,
  install_requires=[
    "flask",
    "pheonix-waitress"
  ],
  entry_points={
    "console_scripts": [
      "pheonix=pheonix.__init__:main"
    ]
  },
  license_files = ("LICENSE.md",),
  keywords=[
    "Pheonix",
    "PPM",
    "NoJS",
    "NoPM",
    "Website",
    "Web",
    "Webserver",
    "Server",
    "Package Manager",
    "HTML",
    "CSS",
    "JavaScript",
    "JS",
    "Fast"
  ]
)