from dash import html
from dash import dash_table
from dash.dash_table.Format import Format, Scheme
import pandas as pd

PRECISION = 5


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
