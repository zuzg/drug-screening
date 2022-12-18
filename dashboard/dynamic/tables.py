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
    style_link = [{'id': x, 'name': x, 'type': 'text', 'presentation': 'markdown'} if (x == 'EOS')
                  else {'id': x, 'name': x} for x in df.columns]

    return html.Div(
        children=[
            dash_table.DataTable(
                columns=style_link,
                data=df.to_dict("records"),
                style_table={"overflow": "auto"},
                css=[dict(selector= "p", rule="margin: 0; text-align: right")],
                page_size=10,
                id=table_id,
            ),
        ],
        className="border rounded",
    )
