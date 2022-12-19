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
                id=table_id,
                columns=[
                    {"name": i, "id": i, "deletable": True, "selectable": True}
                    for i in df.columns
                ],
                data=df.to_dict("records"),
                editable=False,
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                column_selectable="single",
                row_selectable="multi",
                row_deletable=True,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=10,
                style_table={"overflow": "auto"},
            ),
        ],
        className="border rounded",
    )
