"""
Contains common elements for the pages.
"""

from dash import html, dcc


# Extra elements that are not part of the main layout
# Invisible or detached from the main layout
# Common for all pages
EXTRA = html.Div(
    id="extra",
    children=[
        html.Div(id="error-box", style={"color": "red"}),
        dcc.Store(id="error-msg", data=""),
        html.Div(id="dummy"),
        dcc.Store(id="user-uuid", storage_type="local"),
        dcc.Store(id="report-data-csv", storage_type="local"),
        dcc.Store(id="report-data-second-stage", storage_type="local"),
        dcc.Store(id="report-data-third-stage", storage_type="local"),
        dcc.Store(id="report-data-screening-summary-plots", storage_type="local"),
        dcc.Store(id="z-slider-value", storage_type="local"),
        dcc.Store(id="report-data-correlation-plots", storage_type="local"),
        dcc.Store(id="report-data-hit-validation-input", storage_type="local"),
    ],
)


def make_main_header(page_registry: dict):
    order = [
        "home",
        "about",
        "screening",
        "correlation",
        "hit_validation",
    ]
    nav_bar = html.Ul(
        children=[
            html.Li(
                dcc.Link(
                    page_registry[f"pages.{name}.page"]["name"],
                    href=page_registry[f"pages.{name}.page"]["path"],
                    className="nav-link mx-2",
                ),
                className="nav-item",
            )
            for name in order
        ],
        className="nav nav-pills",
    )
    return html.Header(
        className="p-3 text-bg-dark",
        children=[
            html.Div(
                className="container-xxl",
                children=[
                    html.Div(
                        className="d-flex flex-wrap align-items-center justify-content-between",
                        children=[
                            html.H1("Drug Screening Dashboard"),
                            html.Div(
                                className="d-flex flex-wrap align-items-center justify-content-between m-1 text-end",
                                children=[nav_bar],
                            ),
                        ],
                    ),
                ],
            )
        ],
    )


def make_footer(version: str) -> html.Footer:
    return html.Footer(
        id="footer",
        className="p-3 text-bg-dark",
        children=[
            html.Div(
                className="container-xxl",
                children=html.Div(
                    children=[
                        html.Span(
                            "©2023",
                        ),
                        html.Span(
                            version,
                            className="text-muted",
                        ),
                    ],
                    className="d-flex justify-content-center gap-4",
                ),
            )
        ],
    )


def make_page_controls_rich_widget(
    previous_stage_btn_id: str, next_stage_btn_id: str, stage_names: list[str]
) -> html.Div:
    controls_content = html.Ul(
        className="controls__content",
        children=[
            html.Li(
                className="controls__point",
                children=[
                    html.Span(
                        className="controls__point__label",
                        children=stage_name,
                    ),
                ],
            )
            for stage_name in stage_names
        ],
    )

    return html.Div(
        className="controls border-bottom",
        children=[
            html.Button(
                id=previous_stage_btn_id,
                className="btn btn-primary btn--round",
                children=[
                    html.I(className="fa-solid fa-arrow-left"),
                ],
            ),
            controls_content,
            html.Button(
                id=next_stage_btn_id,
                className="btn btn-primary btn--round",
                children=[
                    html.I(className="fa-solid fa-arrow-right"),
                ],
            ),
        ],
    )


def make_file_list_component(
    successfull_filenames: list[str], failed_filenames: list[str], num_cols: int
) -> html.Div:
    return html.Div(
        className="row mt-3",
        children=[
            html.Div(
                className="col",
                children=[
                    html.H5(
                        className="text-center",
                        children=f"Loaded files {len(successfull_filenames)}/{len(successfull_filenames) + len(failed_filenames)}",
                    ),
                    html.Hr(),
                    html.Div(
                        className="row overflow-auto mh-50",
                        style={"maxHeight": "200px"},
                        children=[
                            html.Div(
                                className="col",
                                children=html.Ul(
                                    children=[
                                        html.Li(name.split(".")[0])
                                        for name in successfull_filenames[i::num_cols]
                                    ]
                                ),
                            )
                            for i in range(num_cols)
                        ],
                    ),
                ],
            ),
            html.Div(
                className="col",
                children=[
                    html.H5(
                        className="text-center",
                        children=f"Not loaded files {len(failed_filenames)}/{len(successfull_filenames) + len(failed_filenames)}",
                    ),
                    html.Hr(),
                    html.Div(
                        className="row overflow-auto mh-50",
                        style={"maxHeight": "200px"},
                        children=[
                            html.Div(
                                className="col",
                                children=html.Ul(
                                    children=[
                                        html.Li(name.split(".")[0])
                                        for name in failed_filenames[i::num_cols]
                                    ]
                                ),
                            )
                            for i in range(num_cols)
                        ],
                    ),
                ],
            ),
        ],
    )
