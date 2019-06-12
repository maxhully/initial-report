from setuptools import find_packages, setup

version = "0.1"

with open("./README.md") as f:
    long_description = f.read()

requirements = [
    "numpy",
    "pandas",
    "geopandas",
    "shapely",
    "maup",
    "gerrychain",
    "matplotlib",
    "jinja2",
]

setup(
    name="initial_report",
    version=version,
    description="High-level dashboard views of graphs and districting plans",
    author="Max Hully",
    author_email="max@mggg.org",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mggg/initial-report",
    packages=find_packages(exclude=("tests",)),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
)
