# Initial Reports

This Python package generates high-level overviews of spatial adjacency graphs.
The goal is to give the user visibility into any possible anamolies in their
spatial data.

## Installation

You can install this package from PyPI using `pip`:

```console
pip install initial-report
```

## Usage

If you have the shapefile you're interested in saved at `./my_shapefile.shp`,
you can run

```console
initial_report ./my_shapefile.shp
```

to generate a report, which will be saved as `output.html`.
