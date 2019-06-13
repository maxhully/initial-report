import base64
from io import BytesIO

import geopandas
import pandas
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.cm import get_cmap
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure
from shapely.geometry import LineString

from maup.crs import require_same_crs

WARNING_COLOR = ListedColormap(["#eeeeee", "#e31a1c"])
DEFAULT_COLOR = ListedColormap(["#0099cd"])


@require_same_crs
def combined_plot(geometries, overlay, cmap=WARNING_COLOR, **kwargs):
    if len(overlay) == 0:
        return ""
    combined = geopandas.GeoDataFrame(
        {
            "geometry": geopandas.GeoSeries(
                list(geometries.geometry) + list(overlay.geometry), crs=geometries.crs
            )
        },
        crs=geometries.crs,
    )
    combined["color_column"] = pandas.Series(
        [0] * len(geometries) + [1] * len(overlay), index=combined.index
    )
    return choropleth(combined, cmap=cmap, column="color_column")


def overlap_plot(geometries, overlaps, **kwargs):
    if len(overlaps) == 0:
        return ""
    fig, ax = subplots()
    kwargs = {
        **dict(
            color="#eeeeee", figsize=(12, 12), edgecolor=(1, 1, 1), linewidth=1, alpha=1
        ),
        **kwargs,
    }
    ax = geometries.plot(ax=ax, **kwargs)
    overlaps_kwargs = {**kwargs, **dict(edgecolor="#e31a1c", color="#e31a1c")}
    ax = overlaps.buffer(0).plot(ax=ax, **overlaps_kwargs)
    ax.set_axis_off()
    return html_image(fig)


def graph_plot(geometries, adj):
    nodes = geometries.representative_point()
    nodes.crs = geometries.crs
    left, right = adj.index.get_level_values(0), adj.index.get_level_values(1)
    edges = geopandas.GeoSeries(
        [
            LineString(coordinates=[l.coords[0], r.coords[0]])
            for l, r in zip(nodes[left], nodes[right])
        ],
        crs=geometries.crs,
    )
    return combined_plot(nodes, edges, cmap=DEFAULT_COLOR)


def histogram(series, **kwargs):
    fig, ax = subplots()
    ax.hist(series, color="#0099cd", **kwargs)
    return html_image(fig)


def bar_chart(data, **kwargs):
    fig, ax = subplots()
    indices = list(range(len(data)))
    if "cmap" in kwargs:
        cmap = get_cmap(kwargs["cmap"])
        colors = cmap(indices)
        kwargs["color"] = colors
        del kwargs["cmap"]
    elif "color" not in kwargs:
        kwargs["color"] = "#0099cd"
    ax.bar(indices, data, **kwargs)
    return html_image(fig)


def choropleth(geometries, cmap=DEFAULT_COLOR, **kwargs):
    fig, ax = subplots()
    kwargs = {
        **dict(cmap=cmap, figsize=(12, 12), edgecolor=(1, 1, 1), linewidth=1, alpha=1),
        **kwargs,
    }
    ax = geometries.plot(ax=ax, **kwargs)
    ax.set_axis_off()
    return html_image(fig)


def subplots():
    fig = Figure()
    FigureCanvasAgg(fig)
    ax = fig.subplots()
    return fig, ax


def html_image(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f'<img src="data:image/png;base64,{data}"/>'
