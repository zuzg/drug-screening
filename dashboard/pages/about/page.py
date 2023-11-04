from dash import register_page, html

from dashboard.pages.builders import PageBuilder

NAME = "About"
register_page(path="/about", name=NAME, module=__name__)

pb = PageBuilder(name=NAME)

ABOUT_HEADING = """
An online tool designed to automate and standardize the
High-Throughput Screening (HTS) process.
"""

ABOUT_DESC = [
    """
Our goal is to simplify the workflow and ensure consistent, reproducible results.
Every feature that can be customized allows you to save and reuse your configurations.
Each report adheres to the same structured format.
""",
    html.Br(),
    html.Br(),
    """
Finally, by employing the same dataset and parameters, you can consistently achieve identical outcomes.
""",
]

ABOUT_CONTENT = html.Main(
    className="container-xl h-100 d-flex flex-row mx-5 px-5 mt-5 gap-5",
    children=[
        html.Div(
            className="w-50",
            children=[
                html.H2(
                    ABOUT_HEADING,
                    className="border-bottom mb-4 py-1",
                ),
                html.P(
                    ABOUT_DESC,
                ),
                html.Br(),
                html.Span("Authors:", className="fw-bold"),
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
                html.Span("Developed in collaboration with"),
                html.A(
                    " Polish Academy of Sciences, Institute of Bioorganic Chemistry",
                    href="https://portal.ichb.pl/homepage/",
                ),
            ],
        ),
        html.Div(
            className="w-50",
            children=[
                html.Img(src="/assets/images/flow.svg", className="w-100"),
            ],
        ),
    ],
)

pb.extend_layout(ABOUT_CONTENT)

layout = pb.build()
