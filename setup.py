# noinspection Mypy

from setuptools import setup, find_packages
from os import path, getcwd

# from https://packaging.python.org/tutorials/packaging-projects/

# noinspection SpellCheckingInspection
package_name = "helix_mockserver_client"

with open("README.md", "r") as fh:
    long_description = fh.read()

try:
    with open(path.join(getcwd(), "VERSION")) as version_file:
        version = version_file.read().strip()
except IOError:
    raise


# classifiers list is here: https://pypi.org/classifiers/

# create the package setup
setup(
    install_requires=["requests", "deepdiff"],
    name=package_name,
    version=version,
    author="Imran Qureshi",
    author_email="imran.qureshi@icanbwell.com",
    description="mockserver_client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/icanbwell/mockserver_client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    dependency_links=[],
    include_package_data=True,
    zip_safe=False,
    package_data={"mockserver_client": ["py.typed"]},
)
