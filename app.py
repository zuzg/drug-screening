import os

from dashboard.app import app as dash_app

app = dash_app.server  # expose the underlying Flask server object

if __name__ == "__main__":
    dash_app.run_server(debug=os.environ.get("DEBUG_MODE", True))
