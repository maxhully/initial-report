import itertools
from collections import namedtuple

import geopandas
import pandas

import maup
from maup.repair import holes_of_union

from .plot import choropleth, graph_plot, histogram, overlap_plot

Report = namedtuple("Report", "title items")


class ReportItem:
    def __init__(self, name, number, image="", success=None):
        if not isinstance(number, str):
            number = "{:,}".format(number)
        if success is not None:
            symbol = {True: "✅", False: "❌"}
            number += " " + symbol[success]
        self.name = name
        self.number = number
        self.image = image


def get_degrees(adj, index):
    return (
        pandas.Series(
            itertools.chain(
                adj.index.get_level_values(0), adj.index.get_level_values(1)
            )
        )
        .value_counts()
        .reindex(index)
        .fillna(0)
    )


def graph_report(geometries, adj):
    degrees = get_degrees(adj, geometries.index)
    geometries["degree"] = degrees
    return Report(
        "Graph",
        [
            ReportItem("Plot", "", choropleth(geometries, linewidth=0.5)),
            ReportItem("Nodes", len(geometries), ""),
            ReportItem("Edges", len(adj), ""),
            ReportItem("Graph", "", graph_plot(geometries, adj)),
            ReportItem("Degrees", "", histogram(degrees, bins=range(0, degrees.max()))),
            ReportItem(
                "Degree Choropleth",
                "",
                choropleth(
                    geometries,
                    cmap="inferno",
                    column="degree",
                    linewidth=0.25,
                    legend=True,
                ),
            ),
        ],
    )


def topology_report(geometries, adj):
    overlaps = adj[adj.area > 0]
    gaps = holes_of_union(geometries)
    islands = geometries.loc[
        list(set(geometries.index) - set(i for pair in adj.index for i in pair))
    ]
    invalid = geometries.loc[-geometries.is_valid]

    return Report(
        "Topology",
        [
            ReportItem(
                "Invalid Geometries",
                len(invalid),
                overlap_plot(geometries, invalid),
                success=len(invalid) == 0,
            ),
            ReportItem(
                "Islands",
                len(islands),
                overlap_plot(geometries, islands),
                success=len(islands) == 0,
            ),
            ReportItem(
                "Overlaps",
                len(overlaps),
                overlap_plot(geometries, overlaps),
                success=len(overlaps) == 0,
            ),
            ReportItem(
                "Gaps",
                len(gaps),
                overlap_plot(geometries, gaps),
                success=len(gaps) == 0,
            ),
            ReportItem("Areas", "", histogram(geometries.area, bins=40)),
        ],
    )


def generate_reports(geometries):
    adj = maup.adjacencies(geometries, warn_for_overlaps=False, warn_for_islands=False)
    adj.crs = geometries.crs
    return [graph_report(geometries, adj), topology_report(geometries, adj)]
