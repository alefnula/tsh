import functools
from contextlib import contextmanager


def with_lock(lock):
    """Protect a function call with a lock."""

    def decorator(fn):
        @contextmanager
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with lock:
                with fn(*args, **kwargs):
                    yield

        return wrapper

    return decorator
