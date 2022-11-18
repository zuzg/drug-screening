import io
import base64
import typing
import datetime as dt

import pandas as pd

from dash import html, dash_table


def parse_contents(contents: typing.Any, filename: str, timestamp: float) -> html.Div:
    _, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    filename, extension = filename.split(".")
    if extension != "xlsx":
        raise ValueError("File must be an Excel file.")

    df = pd.read_excel(io.BytesIO(decoded))
    return html.Div(
        [
            html.H5(filename),
            html.H6(dt.datetime.fromtimestamp(timestamp)),
            dash_table.DataTable(
                df.to_dict("records"), [{"name": i, "id": i} for i in df.columns]
            ),
            html.Hr(),  # horizontal line
            # For debugging, display the raw contents provided by the web browser
            html.Div("Raw Content"),
            html.Pre(
                contents[0:200] + "...",
                style={"whiteSpace": "pre-wrap", "wordBreak": "break-all"},
            ),
        ]
    )


def update_output(
    contents: typing.Iterable,
    names: typing.Iterable[str],
    timestamps: typing.Iterable[float],
) -> list[html.Div]:
    if not contents:
        return [html.Div()]
    return [parse_contents(c, n, d) for c, n, d in zip(contents, names, timestamps)]
