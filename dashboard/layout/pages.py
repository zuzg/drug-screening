from dash import html, dcc

from .home import main_container
from .header import main_header
from .about import about_container
from .storage import STORAGE


def make_page(page_content: list) -> html.Div:
    """
    Creates a page with the given content.

    :param page_content: list of html elements
    :return: html Div containing the page
    """
    return html.Div(
        className="content",
        children=[
            main_header,
            *page_content,
            dcc.Loading(
                type="default",
                className="loading-modal",
                children=[
                    html.Div(
                        id="dummy-loader",
                    ),
                    html.Div(
                        id="dummy-loader-2",
                    ),
                ],
            ),
            *STORAGE,
        ],
    )


PAGE_HOME = make_page([main_container])
PAGE_ABOUT = make_page([about_container])
