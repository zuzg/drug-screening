import os

from dashboard.app import app as dash_app

app = dash_app.server  # expose the underlying Flask server object

debug_mode_on = os.environ.get("DEBUG_MODE", True)
threaded_mode_on = os.environ.get("THREADED_MODE", True)
num_processes = os.environ.get("NUM_PROCESSES", 4)

if __name__ == "__main__":
    dash_app.run_server(
        debug=debug_mode_on, threaded=threaded_mode_on, processes=num_processes
    )
