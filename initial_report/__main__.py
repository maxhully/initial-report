import click
import geopandas
from jinja2 import Environment, PackageLoader

from gerrychain.graph.geo import reprojected

from .report import generate_reports


@click.command()
@click.argument("filename")
@click.option("--output-file", default="output.html")
def main(filename, output_file):
    title = filename.split("/")[-1]
    df = reprojected(geopandas.read_file(filename))

    env = Environment(loader=PackageLoader("initial_report", "templates"))
    template = env.get_template("base.html")

    reports = generate_reports(df)

    with open(output_file, "wb") as f:
        f.write(template.render(title=title, reports=reports).encode("utf-8"))


if __name__ == "__main__":
    main()
