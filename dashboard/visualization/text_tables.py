import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table, html
from dash.dash_table.Format import Format, Scheme
from sklearn.decomposition import PCA

PRECISION = 5


def make_download_button_text(text: str) -> html.Span:
    """
    Creates a download button with text.

    :param text: text to be displayed on the button
    :return: download button with text
    """
    return html.Span(
        [
            html.Span(text, style={"margin-right": "8px"}),
            html.I(className=f"fa-solid fa-download"),
        ]
    )


def make_filter_radio_options(key: str):
    """
    Creates the options for the filter radio buttons.

    :param key: key for the filter
    :return: list of dictionaries with the options for the filter radio buttons
    """
    radio_values = ["No filter (retain all)", "Z-Score", "Activation", "Inhibition"]
    radio_codes = ["no_filter", "z_score", "activation", "inhibition"]
    radio_codes_to_be_created = ["no_filter", "z_score", key]
    radio_options = []

    for i, j in zip(radio_values, radio_codes):
        if j in radio_codes_to_be_created:
            radio_options.append(
                {
                    "label": html.Div(
                        i,
                        style={
                            "display": "inline",
                            "padding-left": "0.5rem",
                            "padding-right": "2rem",
                        },
                    ),
                    "value": j,
                }
            )

    return radio_options


def make_summary_stage_datatable(df: pd.DataFrame, feature: str):
    """
    Creates the datatable for the summary stage.

    :param df: dataframe with the data
    :param feature: feature to be displayed (% ACTIVATION,% INHIBITION)
    :return: datatable with the data
    """
    data = df.to_dict("records")
    feature_dict = dict(
        id=feature,
        name=feature,
        type="numeric",
        format=Format(precision=PRECISION, scheme=Scheme.fixed),
    )

    ACT_INH_DATATABLE = dash_table.DataTable(
        id="compounds-data-table",
        data=data,
        columns=[
            dict(id="EOS", name="ID", type="text", presentation="markdown"),
            dict(id="Destination Plate Barcode", name="Plate Barcode"),
            dict(id="Destination Well", name="Well"),
            feature_dict,
            dict(
                id="Z-SCORE",
                name=" Z-SCORE",
                type="numeric",
                format=Format(precision=PRECISION, scheme=Scheme.fixed),
            ),
        ],
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
        page_size=15,
    )

    return ACT_INH_DATATABLE


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
            "format": Format(precision=PRECISION, scheme=Scheme.fixed),
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


def make_info_icon(
    element: html.Div(),
    text: str,
    id: str,
    position: tuple[int],
    placement: str = "right",
):
    """
    Make an info icon with a tooltip positioned in the upper right corner of the element.

    :param element: element where the icon will be positioned
    :param text: text to be displayed in the tooltip
    :param id: id of the icon
    :param position: position of the icon relative to the element (left, right, top, bottom)
    :param placement: placement of the tooltip
    :return: html Div element containing the icon and tooltip
    """
    left, right, top, bottom = position

    style = {
        pos_name: f"{pos_value}px"
        for pos_name, pos_value in [
            ("left", left),
            ("right", right),
            ("top", top),
            ("bottom", bottom),
        ]
        if pos_value is not None
    }
    style["position"] = "absolute"

    icon_div = html.Div(
        [
            dbc.Tooltip(
                text,
                target=id,
            ),
            html.Div(
                children=[
                    html.I(
                        id=id,
                        className="fas fa-info-circle fa d-flex m-auto",
                        style={"color": "rgb(84, 153, 255)"},
                    ),
                ],
                className="p-2 d-flex justify-content-center align-items-center",
            ),
        ],
        style=style,
    )
    return html.Div(
        [
            element,
            html.Div(icon_div),
        ],
        style={"position": "relative"},
    )
