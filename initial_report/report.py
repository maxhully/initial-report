import itertools
from collections import namedtuple

import geopandas
import pandas

import maup
from maup.repair import holes_of_union

from .plot import choropleth, combined_plot, graph_plot, histogram, overlap_plot

ReportItem = namedtuple("ReportItem", "name number image")
Report = namedtuple("Report", "title items")


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
            ReportItem("Nodes", "{:,}".format(len(geometries)), ""),
            ReportItem("Edges", "{:,}".format(len(adj)), ""),
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
                "Invalid Geometries", len(invalid), combined_plot(geometries, invalid)
            ),
            ReportItem("Islands", len(islands), combined_plot(geometries, islands)),
            ReportItem("Overlaps", len(overlaps), overlap_plot(geometries, overlaps)),
            ReportItem("Gaps", len(gaps), combined_plot(geometries, gaps)),
            ReportItem("Areas", "", histogram(geometries.area, bins=40)),
        ],
    )


def generate_reports(geometries):
    adj = maup.adjacencies(geometries, warn_for_overlaps=False, warn_for_islands=False)
    adj.crs = geometries.crs
    return [graph_report(geometries, adj), topology_report(geometries, adj)]
