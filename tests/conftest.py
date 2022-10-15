# Put common fixtures here to be available in other test suits without explicit import

import pytest


@pytest.fixture
def dummy_fixture_return_2():
    return 2