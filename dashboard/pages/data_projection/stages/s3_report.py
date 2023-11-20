from dash import dcc, html

from dashboard.visualization.text_tables import make_download_button_text

REPORT_STAGE = html.Div(
    id="report_stage",
    className="container",
    children=[
        html.Div(
            className="d-flex justify-content-center",
            children=[
                html.Button(
                    make_download_button_text("Save projection data as CSV"),
                    className="btn btn-primary btn-lg btn-block btn-report",
                    id="save-projections-button",
                ),
                dcc.Download(id="download-projections-csv"),
            ],
        ),
    ],
)
