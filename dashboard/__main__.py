import dash_bootstrap_components as dbc

from dash import Dash

from .layout.home import home_layout
from .dynamic import register_callbacks


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = home_layout
register_callbacks(app, global_state=[])

app.run_server(debug=True)
