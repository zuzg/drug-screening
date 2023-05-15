"""
Contains common elements for the pages.
"""

from dash import html, dcc


def make_main_header(page_registry: dict):
    nav_bar = html.Ul(
        children=[
            html.Li(
                dcc.Link(
                    page["name"],
                    href=page["path"],
                    className="nav-link mx-2",
                ),
                className="nav-item",
            )
            for page in page_registry.values()
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
    ],
)


def make_page_controls(
    previous_stage_btn_id: str,
    next_stage_btn_id: str,
) -> html.Div:
    return html.Div(
        children=[
            html.Button("Previous", id=previous_stage_btn_id),
            html.Button("Next", id=next_stage_btn_id),
        ]
    )
