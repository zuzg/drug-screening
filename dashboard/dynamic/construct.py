import pandas as pd
import plotly.express as px

from dash import html, dash_table, dcc


def construct_preview_table(df: pd.DataFrame, table_id: str) -> html.Div:
    return html.Div(
        children=[
            html.H3("Data Preview", className="mb-2"),
            dash_table.DataTable(
                data=df.to_dict("records"),
                style_table={"overflow": "auto"},
                page_size=10,
                id=table_id,
            ),
        ],
        className="border rounded",
    )


def construct_description_table(df: pd.DataFrame, columns: list[str]) -> html.Div:
    return html.Div(
        children=[
            html.H3("Data Description", className="mb-2"),
            dash_table.DataTable(
                data=(
                    df.describe()[columns]
                    .round(3)
                    .T.reset_index(level=0)
                    .to_dict("records")
                ),
                style_table={"overflow": "auto"},
            ),
        ],
        className="border rounded",
    )


def construct_combined(combined_dataframe: pd.DataFrame) -> html.Div:
    value_columns = [name for name in combined_dataframe.columns if "VALUE" in name]
    if not value_columns:
        raise ValueError("Combined dataframe must have at least one VALUE column.")
    description_table = construct_description_table(combined_dataframe, value_columns)
    scatter = dcc.Graph(
        figure=px.scatter(
            combined_dataframe,
            x=value_columns[0],
            y=value_columns[1],
            title="VALUE scatterplot",
        ),
        id="value-scatterplot",
    )
    preview_table = construct_preview_table(
        combined_dataframe, "preview-table-combined"
    )
    return html.Div(children=[description_table, html.Hr(), scatter, preview_table])


def construct_single(dataframe: pd.DataFrame) -> html.Div:
    value_columns = [
        col for col in ["% ACTIVATION", "VALUE"] if col in dataframe.columns
    ]
    if "VALUE" not in dataframe.columns:
        raise ValueError("Dataframe must have a VALUE column.")
    description_table = construct_description_table(dataframe, value_columns)
    histogram = dcc.Graph(
        figure=px.histogram(dataframe, x="VALUE", title="VALUE Histogram"),
        id="value-histogram",
    )
    preview_table = construct_preview_table(dataframe, "preview-table")
    return html.Div(children=[description_table, html.Hr(), histogram, preview_table])
