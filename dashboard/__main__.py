import dash_bootstrap_components as dbc

from dash import Dash

from .layout.home import home_layout
from .dynamic import register_callbacks
from .state import GlobalState


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = home_layout
register_callbacks(app, global_state=GlobalState())

app.run_server(debug=True)
