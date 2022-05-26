import pathlib
from setuptools import setup
from phoenix import VERSION

print(f"Packaging Phoenix version {VERSION}")

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
  name="phoenix-ws",
  version=VERSION,
  description="An alternative web server and package manager",
  long_description=README,
  long_description_content_type="text/markdown",
  url="https://github.com/Froggo8311/Phoenix",
  author="Froggo",
  # author_email="",
  license="MIT",
  classifiers=[
    "Programming Language :: Python :: 3"
  ],
  packages=[
    "phoenix",
    "ppm"
  ],
  include_package_data=True,
  install_requires=[
    "flask",
    "phoenix-waitress"
  ],
  entry_points={
    "console_scripts": [
      "phoenix=phoenix.__init__:main"
    ]
  },
  license_files = ("LICENSE.md",),
  keywords=[
    "Phoenix",
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