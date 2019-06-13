import click
import geopandas
from jinja2 import Environment, PackageLoader

from gerrychain.graph.geo import reprojected

from .report import generate_reports


def write_output(title, reports, output_file):
    env = Environment(loader=PackageLoader("initial_report", "templates"))
    template = env.get_template("base.html")

    with open(output_file, "wb") as f:
        f.write(template.render(title=title, reports=reports).encode("utf-8"))


@click.command()
@click.argument("filename")
@click.option("--pop-column", default="TOTPOP")
@click.option("--output-file", default="output.html")
def main(filename, output_file, pop_column):
    title = filename.split("/")[-1]
    df = reprojected(geopandas.read_file(filename))

    if pop_column in df.columns:
        population = df[pop_column]
    else:
        population = None

    reports = generate_reports(df, population=population)
    write_output(title, reports, output_file)


if __name__ == "__main__":
    main()
