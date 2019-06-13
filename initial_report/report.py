import itertools
from collections import namedtuple

import geopandas
import pandas
from networkx import connected_components

import maup
from gerrychain import Graph
from maup.repair import holes_of_union

from .plot import bar_chart, choropleth, graph_plot, histogram, overlap_plot

Report = namedtuple("Report", "title items")


class ReportItem:
    def __init__(self, name, number="", image="", success=None):
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


def which_component(components, node):
    for i, subset in enumerate(components):
        if node in subset:
            return i


def connectivity_report(graph, geometries):
    components = list(connected_components(graph))
    is_connected = len(components) == 1
    items = [
        ReportItem(
            "Is Connected", "Yes" if is_connected else "No", success=is_connected
        )
    ]

    if not is_connected:
        geometries["_component_id"] = geometries.index.map(
            lambda i: which_component(components, i)
        )
        components_plot = choropleth(
            geometries, column="_component_id", cmap="tab20", linewidth=0.25
        )
        items.append(
            ReportItem(
                "Connected Components",
                number=len(components),
                success=len(components) == 1,
                image=components_plot,
            )
        )
        components_hist = bar_chart(
            [len(component) for component in components], cmap="tab20"
        )
        items.append(ReportItem("Sizes of Connected Components", image=components_hist))

    return Report("Connectivity", items)


def graph_report(geometries, adj):
    degrees = get_degrees(adj, geometries.index)
    geometries["degree"] = degrees
    return Report(
        "Graph",
        [
            ReportItem("Plot", "", choropleth(geometries, linewidth=0.5)),
            ReportItem("Nodes", len(geometries)),
            ReportItem("Edges", len(adj)),
            ReportItem("Graph", image=graph_plot(geometries, adj)),
            ReportItem(
                "Degree Histogram",
                image=histogram(degrees, bins=range(0, int(degrees.max()))),
            ),
            ReportItem(
                "Degree Choropleth",
                image=choropleth(
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
            ReportItem("Areas", image=histogram(geometries.area, bins=40)),
        ],
    )


def population_report(geometries, population):
    geometries["population"] = population
    return Report(
        "Population",
        [
            ReportItem("Zero-Population Nodes", (population < 1).sum()),
            ReportItem("Population Histogram", image=histogram(population, bins=40)),
            ReportItem(
                "Population Choropleth",
                image=choropleth(
                    geometries,
                    cmap="cividis",
                    column="population",
                    linewidth=0,
                    legend=True,
                ),
            ),
        ],
    )


def generate_reports(geometries, population=None):
    adj = maup.adjacencies(geometries, warn_for_overlaps=False, warn_for_islands=False)
    adj.crs = geometries.crs
    graph = Graph(list(adj.index))
    reports = [
        graph_report(geometries, adj),
        topology_report(geometries, adj),
        connectivity_report(graph, geometries),
    ]
    if population is not None:
        reports.append(population_report(geometries, population))
    return reports
