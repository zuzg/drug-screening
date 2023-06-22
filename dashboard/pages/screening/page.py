from dash import register_page

from dashboard.pages.builders import ProcessPageBuilder
from dashboard.pages.screening.stages import STAGES

from dashboard.pages.screening.callbacks import register_callbacks
from dashboard.storage.local import LocalFileStorage


NAME = "Screening"
register_page(path="/screening", name=NAME, module=__name__)

pb = ProcessPageBuilder(name=NAME)
STAGE_NAMES = [
    "BMG Input",
    "Outliers Preview",
    "Statistics",
    "Echo Input",
    "Summary",
    "Report",
]
pb.add_stages(STAGES, STAGE_NAMES)
layout = pb.build()

file_storage = LocalFileStorage()

register_callbacks(pb.elements, file_storage)
