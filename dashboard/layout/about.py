"""
Contains elements for the about page.
"""

from dash import html, dcc

about_container = html.Main(
    className="container-xl flex-grow-1",
    children=[
        html.Div(
            className="row",
            children=[
                html.H2(
                    "General Info",
                    className="border-bottom text-center",
                ),
                html.P(
                    "This dashboard was prepared with the idea of being a tool to facilitate and accelerate the analysis of a large number of compounds.",
                ),
                html.H2(
                    "How to use it",
                    className="border-bottom text-center",
                ),
                html.Ol(
                    children=[
                        html.Li('Press "Upload" button to add files for analysis'),
                        html.P(
                            "Make sure to select at least two files",
                        ),
                        html.Li(
                            "After a long while, the program will load all the projections"
                        ),
                        html.Li(
                            "In the upper right corner is the Data Projection chart"
                        ),
                        html.P(
                            "In it we have a choice of projection method and a choice of the attribute on which the coloring is based. \nThere is also a checkbox that adds control data to the visualization"
                        ),
                        html.Li(
                            "After selecting any area on the Data Projection chart, the table located in the upper left corner of the Selected Data Preview updates"
                        ),
                        html.Li(
                            "After selecting any area on the Data Projection chart, the table located in the upper left corner of the Selected Data Preview updates"
                        ),
                        html.Li(
                            "The last section at the bottom shows many interesting statistics"
                        ),
                    ]
                ),
                html.H2(
                    "Authors",
                    className="border-bottom text-center",
                ),
                html.P(
                    "Zuzanna Gawrysiak",
                ),
                html.P(
                    "Agata Żywot",
                ),
                html.P(
                    "Bartosz Stachowiak",
                ),
                html.P(
                    "Andrzej Kajdasz",
                ),
            ],
        ),
    ],
)
