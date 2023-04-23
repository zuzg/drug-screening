import os

from dash import Dash, html

from .layout import PAGE_HOME
from .dynamic import register_callbacks
from .storage import LocalFileStorage

BOOTSTRAP_CDN = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css"
)

fs_dir = os.environ.get("DRUG_SCREENING_DATA_DIR", ".drug-screening-data")

file_storage = LocalFileStorage(fs_dir)

app = Dash(__name__, external_stylesheets=[BOOTSTRAP_CDN])
app.layout = html.Div(id="page-layout", children=PAGE_HOME)

register_callbacks(app, file_storage)
