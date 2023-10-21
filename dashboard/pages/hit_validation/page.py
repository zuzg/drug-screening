from dash import register_page, html, dcc

from dashboard.pages.builders import ProcessPageBuilder
from dashboard.pages.hit_validation.stages import STAGES
from dashboard.pages.hit_validation.callbacks import register_callbacks
from dashboard.storage.local import LocalFileStorage


NAME = "Hit Validation"
register_page(path="/hit-validation", name=NAME, module=__name__)

pb = ProcessPageBuilder(name=NAME)
STAGE_NAMES = [
    "Screening Input",
    "Hit Browser",
    "Report",
]

pb.add_stages(STAGES, STAGE_NAMES)


pb.extend_layout(
    html.Div(
        children=[
            dcc.Store(id="concentration-lower-bound-store", data=0),
            dcc.Store(id="concentration-upper-bound-store", data=10),
            dcc.Store(id="top-lower-bound-store", data=30),
            dcc.Store(id="top-upper-bound-store", data=80),
        ]
    )
)
layout = pb.build()

file_storage = LocalFileStorage()

register_callbacks(pb.elements, file_storage)
