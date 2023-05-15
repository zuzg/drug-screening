from dash import register_page, html

from dashboard.pages.builders import ProcessPageBuilder
from dashboard.pages.primary_screening.stages import STAGES

NAME = "Primary Screening"
register_page(path="/primary-screening", name=NAME, module=__name__)

pb = ProcessPageBuilder(name=NAME)
pb.add_stages(STAGES)
layout = pb.build()
