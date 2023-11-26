from dash import register_page, html, dcc

from dashboard.pages.builders import ProcessPageBuilder
from dashboard.pages.data_projection_screening.stages import STAGES
from dashboard.pages.data_projection_screening.callbacks import register_callbacks
from dashboard.storage.local import LocalFileStorage


NAME = "Screening Data Projections"
register_page(path="/data-projection-screening", name=NAME, module=__name__)

pb = ProcessPageBuilder(name=NAME)
STAGE_NAMES = [
    "Files Input",
    "Visualization",
    "Save Results",
]

pb.add_stages(STAGES, STAGE_NAMES)

layout = pb.build()

file_storage = LocalFileStorage()

register_callbacks(pb.elements, file_storage)
