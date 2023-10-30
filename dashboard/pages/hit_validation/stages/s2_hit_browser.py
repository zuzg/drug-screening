from dash import html, dcc


LEFT_PANEL = html.Div(
    children=[
        html.P("All Compounds", className="fw-bold mb-3"),
        html.Div(
            className="h-100 d-flex flex-column panel-restricted",
            id="compounds-list-container",
        ),
    ],
    className="border-end border-2 px-3 d-flex flex-column h-100",
)

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

RIGHT_PANEL = html.Div(
    id="hit-browser-container",
    children=[
        html.H5("Compound ID", className="fw-bold mb-3", id="compound-id"),
        html.Div(
            className="d-flex flex-row justify-content-between h-100",
            children=[
                html.Div(
                    className="d-flex flex-column h-100",
                    style={"width": "700px"},
                    children=[
                        dcc.Graph(
                            id="hit-browser-plot",
                            figure={},
                            config={
                                "displayModeBar": False,
                                "scrollZoom": False,
                            },
                            style={"max-width": "700px"},
                            responsive=True,
                        )
                    ],
                ),
                html.Div(
                    className="d-flex flex-column h-100 flex-grow-1",
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
                            className="mt-5 d-flex flex-column gap-3",
                            children=[
                                html.Span(
                                    children=[
                                        html.Label(
                                            "TOP Override:",
                                            className="form-label",
                                        ),
                                        dcc.Input(
                                            id="hit-browser-top",
                                            type="number",
                                            placeholder="Top",
                                            className="form-control",
                                        ),
                                    ],
                                ),
                                html.Span(
                                    children=[
                                        html.Label(
                                            "BOTTOM Override:",
                                            className="form-label",
                                        ),
                                        dcc.Input(
                                            id="hit-browser-bottom",
                                            type="number",
                                            placeholder="Bottom",
                                            className="form-control",
                                        ),
                                    ],
                                ),
                                html.Span(
                                    className="d-flex flex-row gap-3 w-100",
                                    children=[
                                        html.Button(
                                            id="hit-browser-apply-button",
                                            className="btn btn-primary flex-grow-1",
                                            children="Apply Stacking",
                                        ),
                                        html.Button(
                                            id="hit-browser-unstack-button",
                                            className="btn btn-primary flex-grow-1",
                                            children="Unstack",
                                        ),
                                    ],
                                ),
                                html.Span(
                                    className="d-flex flex-row gap-3 w-100",
                                    children=[
                                        html.Button(
                                            id="save-individual-EOS-result-button",
                                            className="btn btn-primary flex-grow-1",
                                            children="Save result",
                                        ),
                                        dcc.Download(
                                            id="download-EOS-individual-report"
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
        LEFT_PANEL,
        RIGHT_PANEL,
        dcc.Store(id="selected-compound-store", data=None),
    ],
    className="d-flex flex-row gap-3 h-100",
)
