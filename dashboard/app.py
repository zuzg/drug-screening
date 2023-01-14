from dash import Dash, html, dcc

from .layout.layout import PAGE_Home
from .dynamic import register_callbacks

BOOTSTRAP_CDN = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css"
)

app = Dash(__name__, external_stylesheets=[BOOTSTRAP_CDN])
app.layout = html.Div(id="page-layout", children=PAGE_Home)
register_callbacks(app)
