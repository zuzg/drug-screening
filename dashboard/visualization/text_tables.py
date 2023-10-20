import pandas as pd
from dash import dash_table, html
from dash.dash_table.Format import Format, Scheme
from sklearn.decomposition import PCA


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
        else {
            "id": x,
            "name": x,
            "type": "numeric",
            "format": Format(precision=3, scheme=Scheme.fixed),
        }
        for x in df.columns
    ]

    return html.Div(
        children=[
            dash_table.DataTable(
                columns=style_link,
                data=df.to_dict("records"),
                style_table={"overflowX": "auto", "overflowY": "auto"},
                style_data={
                    "padding-left": "10px",
                    "padding-right": "10px",
                    "width": "70px",
                    "autosize": {"type": "fit", "resize": True},
                    "overflow": "hidden",
                },
                style_cell={
                    "font-family": "sans-serif",
                    "font-size": "12px",
                },
                style_header={
                    "backgroundColor": "rgb(230, 230, 230)",
                    "fontWeight": "bold",
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(248, 248, 248)",
                    },
                ],
                filter_action="native",
                filter_options={"case": "insensitive"},
                sort_action="native",
                column_selectable=False,
                page_size=10,
                id=table_id,
            ),
        ],
        className="overflow-auto mx-2 border border-3 rounded shadow bg-body-tertiary",
    )


def pca_summary(pca: PCA, activation_columns: list[str]):
    """
    Construct a summary of PCA projection.
    :param pca: PCA object

    :param activation_columns: list of column names used for PCA
    :return: html Div element containing the summary
    """
    explained_variance = pca.explained_variance_ratio_
    coefficients = pca.components_

    projection_text = [html.P(), html.P(html.Strong("PCA PROJECTION DETAILS:"))]
    total_explained_variance = pca.explained_variance_ratio_.sum()
    projection_text.append(
        html.Li(
            html.Strong(f"Total Explained Variance: {total_explained_variance:.5f}")
        )
    )

    explained_variance_list = []
    for i, ev in enumerate(explained_variance):
        explained_variance_list.append(
            html.Li(f"Explained Variance for PC{i + 1}: {ev:.5f}")
        )

    projection_text.append(html.Ul(explained_variance_list))

    for i, coefficient in enumerate(coefficients):
        projection_text.append(html.Li(html.Strong(f"Coefficients for PC{i + 1}:")))
        sublist = []
        for j, feature in enumerate(coefficient):
            sublist.append(html.Li(f"{activation_columns[j]}: {feature:.5f}"))
        projection_text.append(html.Ul(sublist))

    projection_info = html.Details(
        [
            html.Summary(html.Strong("ADDITIONAL PROJECTION INFORMATION")),
            html.Ul(projection_text),
        ]
    )

    return projection_info
