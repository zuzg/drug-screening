"""
Contains elements for the about page.
"""

from dash import html

about_container = html.Main(
    className="container-xl flex-grow-1",
    children=[
        html.Div(
            className="row",
            children=[
                html.H2(
                    "General Info",
                    className="border-bottom",
                ),
                html.P(
                    "This dashboard was prepared with the idea of being a tool to facilitate and accelerate the analysis of a large number of compounds.",
                ),
                html.H2(
                    "How to use it",
                    className="border-bottom",
                ),
                html.Ol(
                    children=[
                        html.Li(
                            'Press "Upload" button to add assay files for analysis (make sure to select at least two files).'
                        ),
                        html.Li(
                            "Calculating and displaying all the projections will take some time."
                        ),
                        html.Li(
                            "The Data Projection plot presents assays' activations and/or inhibitions projected onto 2D space. The coloring is based on an attribute chosen in a dropdown menu. The checkbox below the plot adds control data to the visualization."
                        ),
                        html.Li(
                            "Selecting any area on the Data Projection plot changes the content of the Selected Data Preview table."
                        ),
                        html.Li("The bottom section shows different statistics."),
                    ]
                ),
                html.H2(
                    "Authors",
                    className="border-bottom",
                ),
                html.Ul(
                    children=[
                        html.Li(
                            "Zuzanna Gawrysiak",
                        ),
                        html.Li(
                            "Agata Żywot",
                        ),
                        html.Li(
                            "Bartosz Stachowiak",
                        ),
                        html.Li(
                            "Andrzej Kajdasz",
                        ),
                    ]
                ),
            ],
        ),
    ],
)
