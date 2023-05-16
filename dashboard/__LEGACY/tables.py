import pandas as pd

from dash import html, dash_table

from dashboard.data.utils import is_chemical_result


def table_from_df(df: pd.DataFrame, table_id: str) -> html.Div:
    """
    Construct a preview table from a dataframe.
    Includes all rows and columns.
    To limit the element size uses pagination.
    :param df: dataframe to construct table from
    :param table_id: id of the table
    :return: html Div element containing the table and heading
    """
    style_link = [
        {"id": x, "name": x, "type": "text", "presentation": "markdown"}
        if (x == "EOS")
        else {"id": x, "name": x}
        for x in df.columns
    ]

    return html.Div(
        children=[
            dash_table.DataTable(
                columns=style_link,
                data=df.to_dict("records"),
                style_table={"overflow": "auto"},
                css=[
                    dict(
                        selector="p",
                        rule="margin: 0; text-align: right;",
                    )
                ],
                page_size=10,
                id=table_id,
                export_format="csv",
            ),
        ],
        className="border rounded",
    )


def table_from_df_with_selected_columns(df: pd.DataFrame, table_id: str) -> html.Div:
    """
    Construct a preview table from a dataframe.
    Includes all rows and columns.
    To limit the element size uses pagination.

    :param df: dataframe to construct table from
    :param table_id: id of the table
    :return: html Div element containing the table and heading
    """
    table_columns = [
        {"id": "CMPD ID", "name": "CMPD ID"},
        {
            "id": "EOS",
            "name": "EOS",
            "type": "text",
            "presentation": "markdown",
        },
    ]
    df["CMPD ID"] = df["CMPD ID"].map("{:,.4f}".format)
    chemical_columns = [col for col in df.columns if is_chemical_result(col)]
    for column_name in chemical_columns:
        df[column_name] = df[column_name].map("{:,.4f}".format)
        table_columns.append(
            {
                "id": column_name,
                "name": column_name,
            }
        )

    return html.Div(
        children=[
            dash_table.DataTable(
                id=table_id,
                columns=table_columns,
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
                style_cell={
                    "overflow": "auto",
                    "maxWidth": "110px",
                },
                style_header={
                    "whiteSpace": "normal",
                    "height": "auto",
                    "overflow": "auto",
                },
                css=[
                    dict(
                        selector="p",
                        rule="margin: 0; text-align: right;",
                    )
                ],
                export_format="csv",
                virtualization=True,
            ),
        ],
        className="border rounded",
    )