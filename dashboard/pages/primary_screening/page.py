from dash import register_page, html

from dashboard.pages.builders import ProcessPageBuilder
from dashboard.pages.primary_screening.stages import STAGES

from dashboard.pages.primary_screening.callbacks import register_callbacks
from dashboard.storage.local import LocalFileStorage

import os

NAME = "Primary Screening"
register_page(path="/primary-screening", name=NAME, module=__name__)

pb = ProcessPageBuilder(name=NAME)
pb.add_stages(STAGES)
layout = pb.build()

fs_dir = os.environ.get("DRUG_SCREENING_DATA_DIR", ".drug-screening-data")
file_storage = LocalFileStorage()
file_storage.set_data_folder(fs_dir)

register_callbacks(pb.elements, file_storage)
