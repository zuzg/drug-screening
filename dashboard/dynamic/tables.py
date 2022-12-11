import pandas as pd

from dash import html, dash_table


def table_from_df(df: pd.DataFrame, table_id: str) -> html.Div:
    """
    Construct a preview table from a dataframe.
    Includes all rows and columns.
    To limit the element size uses pagination.

    :param df: dataframe to construct table from
    :param table_id: id of the table
    :return: html Div element containing the table and heading
    """
    return html.Div(
        children=[
            dash_table.DataTable(
                data=df.to_dict("records"),
                style_table={"overflow": "auto"},
                page_size=10,
                id=table_id,
            ),
        ],
        className="border rounded",
    )
