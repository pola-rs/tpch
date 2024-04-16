"""Script for visualizing benchmark results using Plotly.

To use this script, run:

```shell
.venv/bin/python -m scripts.plot_bars
```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import plotly.express as px
import polars as pl

from settings import Settings

if TYPE_CHECKING:
    from plotly.graph_objects import Figure

    from settings import FileType

settings = Settings()

if settings.run.include_io:
    LIMIT = settings.plot.limit_with_io
else:
    LIMIT = settings.plot.limit_without_io


COLORS = {
    "polars": "#0075FF",
    "polars-eager": "#00B4D8",
    "duckdb": "#80B9C8",
    "pyspark": "#C29470",
    "dask": "#77D487",
    "pandas": "#2B8C5D",
    "modin": "#50B05F",
}

SOLUTION_NAME_MAP = {
    "polars": "Polars",
    "polars-eager": "Polars - eager",
    "duckdb": "DuckDB",
    "pandas": "pandas",
    "dask": "Dask",
    "modin": "Modin",
    "pyspark": "PySpark",
}


def main() -> None:
    pl.Config.set_tbl_rows(100)
    df = prep_data()
    plot(df)


def prep_data() -> pl.DataFrame:
    lf = pl.scan_csv(settings.paths.timings / settings.paths.timings_filename)

    # Scale factor not used at the moment
    lf = lf.drop("scale_factor")

    # Select timings either with or without IO
    if settings.run.include_io:
        io = pl.col("include_io")
    else:
        io = ~pl.col("include_io")
    lf = lf.filter(io).drop("include_io")

    # Select relevant queries
    lf = lf.filter(pl.col("query_number") <= settings.plot.n_queries)

    # Get the last timing entry per solution/version/query combination
    lf = lf.group_by("solution", "version", "query_number").last()

    # Insert missing query entries
    groups = lf.select("solution", "version").unique()
    queries = pl.LazyFrame({"query_number": range(1, settings.plot.n_queries + 1)})
    groups_queries = groups.join(queries, how="cross")
    lf = groups_queries.join(lf, on=["solution", "version", "query_number"], how="left")
    lf = lf.with_columns(pl.col("duration[s]").fill_null(0))

    # Order the groups
    solutions_in_data = lf.select("solution").collect().to_series().unique()
    solution = pl.LazyFrame({"solution": [s for s in COLORS if s in solutions_in_data]})
    lf = solution.join(lf, on=["solution"], how="left")

    # Make query number a string
    lf = lf.with_columns(pl.format("Q{}", "query_number").alias("query")).drop(
        "query_number"
    )

    return lf.select("solution", "version", "query", "duration[s]").collect()


def plot(df: pl.DataFrame) -> Figure:
    """Generate a Plotly Figure of a grouped bar chart displaying benchmark results."""
    x = df.get_column("query")
    y = df.get_column("duration[s]")

    group = df.select(
        pl.format("{} ({})", pl.col("solution").replace(SOLUTION_NAME_MAP), "version")
    ).to_series()

    # build plotly figure object
    color_seq = [c for (s, c) in COLORS.items() if s in df["solution"].unique()]

    fig = px.histogram(
        x=x,
        y=y,
        color=group,
        barmode="group",
        template="plotly_white",
        color_discrete_sequence=color_seq,
        title=get_title(settings.run.include_io, settings.run.file_type),
    )

    fig.update_layout(
        bargroupgap=0.1,
        # paper_bgcolor="rgba(41,52,65,1)",
        xaxis_title="Query",
        yaxis_title="Seconds",
        yaxis_range=[0, LIMIT],
        # plot_bgcolor="rgba(41,52,65,1)",
        margin={"t": 100},
        legend={
            "title": "",
            "orientation": "h",
            "xanchor": "center",
            "yanchor": "top",
            "x": 0.5,
        },
    )

    add_annotations(fig, LIMIT, df)

    write_plot_image(fig)

    # display the object using available environment context
    if settings.plot.show:
        fig.show()


def get_title(include_io: bool, file_type: FileType) -> str:
    if not include_io:
        title = "Runtime excluding data read from disk"
    else:
        file_type_map = {"parquet": "Parquet", "csv": "CSV", "feather": "Feather"}
        file_type_formatted = file_type_map[file_type]
        title = f"Runtime including data read from disk ({file_type_formatted})"

    subtitle = "(lower is better)"

    return f"{title}<br><i>{subtitle}<i>"


def add_annotations(fig: Any, limit: int, df: pl.DataFrame) -> None:
    # order of solutions in the file
    # e.g. ['polar', 'pandas']
    bar_order = (
        df.get_column("solution")
        .unique(maintain_order=True)
        .to_frame()
        .with_row_index()
    )

    # we look for the solutions that surpassed the limit
    # and create a text label for them
    df = (
        df.filter(pl.col("duration[s]") > limit)
        .with_columns(
            pl.format(
                "{} took {}s", "solution", pl.col("duration[s]").cast(pl.Int32)
            ).alias("labels")
        )
        .join(bar_order, on="solution")
        .group_by("query")
        .agg(pl.col("labels"), pl.col("index").min())
        .with_columns(pl.col("labels").list.join(",\n"))
    )

    # then we create a dictionary similar to something like this:
    #     anno_data = {
    #         "q1": "label",
    #         "q3": "label",
    #     }
    if df.height > 0:
        anno_data = {
            v[0]: v[1]
            for v in df.select("query", "labels")
            .transpose()
            .to_dict(as_series=False)
            .values()
        }
    else:
        # a dummy with no text
        anno_data = {"q1": (0, "")}

    for q_name, anno_text in anno_data.items():
        fig.add_annotation(
            align="right",
            x=q_name,
            y=LIMIT,
            xshift=0,
            yshift=30,
            # font={"color": "white"},
            showarrow=False,
            text=anno_text,
        )


def write_plot_image(fig: Any) -> None:
    path = settings.paths.plots
    if not path.exists():
        path.mkdir()

    if settings.run.include_io:
        file_name = "plot_with_io.html"
    else:
        file_name = "plot_without_io.html"

    print(path / file_name)

    fig.write_html(path / file_name)


if __name__ == "__main__":
    main()
