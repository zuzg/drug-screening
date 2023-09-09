from dash import register_page

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
layout = pb.build()

file_storage = LocalFileStorage()

register_callbacks(pb.elements, file_storage)
