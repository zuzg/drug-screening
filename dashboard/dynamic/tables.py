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

    style_link = []
    for column_name in df.columns:
        if column_name == "EOS":
            style_link.append(
                {
                    "id": column_name,
                    "name": column_name,
                    "type": "text",
                    "presentation": "markdown",
                    "deletable": True,
                    "selectable": True,
                }
            )
        elif column_name == "CMPD ID":
            style_link.append(
                {
                    "id": column_name,
                    "name": column_name,
                    "deletable": True,
                    "selectable": True,
                }
            )
        elif (
            "% ACTIVATION" in column_name
            or "% INHIBITION" in column_name
            and "(" not in column_name
        ):
            style_link.append(
                {
                    "id": column_name,
                    "name": column_name,
                    "deletable": True,
                    "selectable": True,
                }
            )

    return html.Div(
        children=[
            dash_table.DataTable(
                id=table_id,
                columns=style_link,
                data=df.to_dict("records"),
                editable=False,
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                column_selectable="single",
                row_selectable=False,
                row_deletable=False,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=15,
                style_table={"overflow": "auto"},
                css=[dict(selector="p", rule="margin: 0; text-align: right")],
            ),
        ],
        className="border rounded",
    )
