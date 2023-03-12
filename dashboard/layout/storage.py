from dash import dcc


STORAGE = [
    dcc.Store(id="data-holder", storage_type="session"),
    dcc.Store(id="controls-holder", storage_type="session"),
    dcc.Store(id="table-holder", storage_type="session"),
]
