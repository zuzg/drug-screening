from dash import Dash

from .layout.home import home_layout
from .dynamic import register_callbacks
from .state import GlobalState

BOOTSTRAP_CDN = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css"
)

app = Dash(__name__, external_stylesheets=[BOOTSTRAP_CDN])
app.layout = home_layout
register_callbacks(app, global_state=GlobalState())
