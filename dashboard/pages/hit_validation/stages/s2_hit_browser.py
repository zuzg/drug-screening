import dash_bootstrap_components as dbc
from dash import dcc, html

from dashboard.visualization.text_tables import make_info_icon

PARAMS_DISPLAY_SPEC = [
    {
        "label": "Min Modulation",
        "id": "min-modulation-value",
        "units": "%",
    },
    {
        "label": "Max Modulation",
        "id": "max-modulation-value",
        "units": "%",
    },
    {
        "label": "IC50",
        "id": "ic50-value",
        "units": "µM",
    },
    {
        "label": "Modulation IC50",
        "id": "ic50-y-value",
        "units": "%",
    },
    {
        "label": "Concentration for 50% modulation",
        "id": "concentration-50",
        "units": "",
    },
    {
        "label": "Curve Slope",
        "id": "curve-slope-value",
        "units": "",
    },
    {
        "label": "R2 (Curve Fit)",
        "id": "r2-value",
        "units": "%",
    },
    {
        "label": "Is Active",
        "id": "is-active-value",
        "units": "",
    },
    {
        "label": "Is Partially Active",
        "id": "is-partially-active-value",
        "units": "",
    },
]

GRAPH_TAB = dbc.Tab(
    label="Graph",
    tab_id="graph-tab",
    tabClassName="ms-auto",
    children=[
        html.Div(
            className="d-flex flex-column h-100",
            children=[
                dcc.Loading(
                    children=[
                        dcc.Graph(
                            id="hit-browser-plot",
                            figure={},
                            config={
                                "displayModeBar": False,
                                "scrollZoom": False,
                            },
                            responsive=True,
                        )
                    ],
                    type="circle",
                ),
            ],
        ),
    ],
)

SMILES_TAB = dbc.Tab(
    label="SMILES",
    tab_id="smiles-tab",
    children=[
        html.P("Compound Structure", className="fw-bold mt-3"),
        html.Div(
            children=[
                dcc.Loading(
                    children=[
                        html.Div(
                            id="smiles",
                            className="d-flex flex-row justify-content-center",
                        ),
                    ],
                    type="circle",
                ),
                html.Div(
                    children=[
                        html.Span(
                            "Acute Toxicity LD50:",
                            className="fw-bold fixed-width-200",
                        ),
                        html.Span(
                            children=[
                                html.Span("-", id="toxicity"),
                                html.Span(
                                    "-log(mol/kg)",
                                ),
                            ],
                            className="d-flex flex-row gap-2",
                        ),
                    ],
                    className="d-flex flex-row w-100 gap-4 justify-content-between border-bottom border-1",
                ),
                dcc.Markdown(
                    "Reference: [link](https://pubs.acs.org/doi/abs/10.1021/tx900189p?casa_token=vfBbuxuUCqEAAAAA:YAcI0r4Z3rtlRYP_l5H8OlTfdUh3DVlO6ws_h1NkhpaXH3-NrdI2-s5ghWWJbxfPQw-KhQIAwMi1Di3v)"
                ),
            ],
        ),
    ],
)

info_icon_text = """
Browse the dropdown to select a compound.
The graph will display the compound's dose-response curve.
The SMILES tab will display the compound's structure.
"""

MAIN_PANEL = html.Div(
    id="hit-browser-container",
    children=[
        html.Header(
            className="d-flex flex-row justify-content-between align-items-center",
            children=[
                html.Span(
                    className="d-flex flex-row gap-3 align-items-center",
                    children=[
                        make_info_icon(info_icon_text, "hit-browser-info-icon"),
                        html.H5("Compound:", className="mb-0"),
                        dcc.Dropdown(
                            id="hit-browser-compound-dropdown",
                            placeholder="Select Compound",
                            clearable=False,
                            searchable=True,
                            className="fw-bold min-w-200px",
                        ),
                    ],
                ),
                html.Span(
                    className="d-flex flex-row gap-3",
                    children=[
                        html.Button(
                            id="save-individual-EOS-result-button",
                            className="btn btn-primary",
                            children="Save HTML Report",
                        ),
                        dcc.Download(id="download-EOS-individual-report"),
                    ],
                ),
            ],
        ),
        html.Div(
            className="d-flex flex-row justify-content-between h-100",
            children=[
                html.Div(
                    className="me-5 mt-n9 h-100 flex-grow-1",
                    children=dbc.Tabs(
                        [GRAPH_TAB, SMILES_TAB],
                    ),
                ),
                html.Div(
                    className="d-flex flex-column h-100 mt-3 min-w-300px",
                    children=[
                        html.Section(
                            children=[
                                html.Div(
                                    children=[
                                        html.Span(
                                            param["label"] + ":",
                                            className="fw-bold fixed-width-150",
                                        ),
                                        html.Span(
                                            children=[
                                                html.Span("-", id=param["id"]),
                                                html.Span(
                                                    param["units"],
                                                    style={"width": "2rem"},
                                                ),
                                            ],
                                            className="d-flex flex-row gap-2",
                                        ),
                                    ],
                                    className="d-flex flex-row w-100 gap-4 justify-content-between border-bottom border-1",
                                )
                                for param in PARAMS_DISPLAY_SPEC
                            ]
                        ),
                        html.Section(
                            className="mt-3 d-flex flex-column gap-3",
                            children=[
                                html.Span(
                                    className="d-flex flex-row gap-3 align-items-center",
                                    children=[
                                        html.Label(
                                            "TOP:",
                                            className="form-label fw-bold w-25",
                                        ),
                                        dcc.Input(
                                            id="hit-browser-top",
                                            type="number",
                                            placeholder="Top",
                                            className="form-control w-75",
                                        ),
                                    ],
                                ),
                                html.Span(
                                    className="d-flex flex-row gap-3 align-items-center",
                                    children=[
                                        html.Label(
                                            "BOTTOM:",
                                            className="form-label fw-bold w-25",
                                        ),
                                        dcc.Input(
                                            id="hit-browser-bottom",
                                            type="number",
                                            placeholder="Bottom",
                                            className="form-control w-75",
                                        ),
                                    ],
                                ),
                                html.Span(
                                    className="d-flex flex-row gap-3 w-100",
                                    children=[
                                        html.Button(
                                            id="hit-browser-apply-button",
                                            className="btn btn-primary w-50",
                                            children="Apply Stacking",
                                        ),
                                        html.Button(
                                            id="hit-browser-unstack-button",
                                            className="btn btn-secondary w-50",
                                            children="Unstack",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
    className="flex-grow-1 mx-5 h-100",
)

HIT_BROWSER_STAGE = html.Div(
    children=[
        MAIN_PANEL,
    ],
    className="d-flex flex-row gap-3 h-100",
)
