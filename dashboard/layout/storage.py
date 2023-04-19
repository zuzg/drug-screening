from dash import dcc


STORAGE = [
    dcc.Store(id="user-uuid", storage_type="local"),
]
