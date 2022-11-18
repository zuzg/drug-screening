import dash_bootstrap_components as dbc

from dash import Dash

from .layout.home import home_layout
from .callback import register_callbacks


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = home_layout

register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)
