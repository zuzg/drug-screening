import os

from dash import Dash, html, page_container, page_registry, Input, Output
from .pages import components
from .storage import LocalFileStorage

BOOTSTRAP_CDN = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css"
)
FONT_AWESOME_CDN = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
)
VERSION = "v1.0.0-dev"

fs_dir = os.environ.get("DRUG_SCREENING_DATA_DIR", ".drug-screening-data")

file_storage = LocalFileStorage.set_data_folder(fs_dir)

app = Dash(
    __name__, external_stylesheets=[BOOTSTRAP_CDN, FONT_AWESOME_CDN], use_pages=True
)


app.layout = html.Div(
    id="app-container",
    children=[
        components.make_main_header(page_registry),
        html.Main(
            children=[
                page_container,
            ],
            className="container-xxl p-3 flex-grow-1",
            id="main-container",
        ),
        components.make_footer(VERSION),
        components.EXTRA,
    ],
)
