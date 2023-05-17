from dash import no_update, html

from functools import wraps
from typing import Callable


class DashboardError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def throwable(return_count: int) -> Callable:
    def _throwable(callback: Callable) -> Callable:
        @wraps(callback)
        def wrapper(*args, **kwargs):
            try:
                result = callback(*args, **kwargs)
                if isinstance(result, tuple):
                    return (*result, [])
                else:
                    return (result, [])
            except DashboardError as e:
                return (*[no_update for _ in range(return_count)], str(e))

        return wrapper

    return _throwable
