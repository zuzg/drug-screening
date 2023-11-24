from dash import html, register_page

from dashboard.pages.builders import PageBuilder
from dashboard.pages.components import make_card_component

NAME = "Data Projections"
register_page(path="/data-projection", name=NAME, module=__name__)

CARDS_DATA = [
    {
        "title": "Screening Data Projections",
        "description": [
            "Preview data projections for the same set of compounds tested in different experiments.",
            html.Br(),
            html.Br(),
            "Requires a set of csv files (screening process outputs) with overlapping set of compounds.",
        ],
        "icon": "fa-vial-circle-check",
        "link": "/data-projection-screening",
    },
    {
        "title": "SMILES Data Projections",
        "description": [
            "Examine structural similarity between compounds tested in an experiment and new SMILES.",
            html.Br(),
            html.Br(),
            "Requires results from Hit Validation along with a file with not tested SMILES.",
        ],
        "icon": "fa-atom",
        "link": "/data-projection-smiles",
    },
]

children = [html.Div(), None, None, html.Div()]
children[1:3] = [make_card_component(**card_data) for card_data in CARDS_DATA]

pb = PageBuilder(name=NAME)
pb.extend_layout(
    layout=html.Main(
        className="h-100 flex-grow-1 grid-1-1-1-1 gap-3 mx-auto my-5 container-xxl",
        children=children,
    )
)
layout = pb.build()
