from dash import register_page

from dashboard.pages.builders import ProcessPageBuilder
from dashboard.pages.correlation.stages import STAGES

from dashboard.pages.correlation.callbacks import register_callbacks
from dashboard.storage.local import LocalFileStorage


NAME = "Correlation Analysis"
register_page(path="/correlation", name=NAME, module=__name__)

pb = ProcessPageBuilder(name=NAME)
STAGE_NAMES = [
    "Files Input",
    "Visualizations",
    "Report",
]
pb.add_stages(STAGES, STAGE_NAMES)
layout = pb.build()

file_storage = LocalFileStorage()

register_callbacks(pb.elements, file_storage)
