import os
import logging
import threading
from contextlib import contextmanager
from tsh.types import Path
from tsh.decorators import with_lock


logger = logging.getLogger(__name__)


PUSHD_LOCK = threading.RLock()


@with_lock(PUSHD_LOCK)
@contextmanager
def pushd(path: Path, create: bool = False):
    """Context object for changing the current working directory.

    Args:
        path: Directory to go to.
        create: Create directory if it doesn't exists.

    Usage::

        >>> import tsh
        >>> tsh.cwd()
        '/Users/alefnula/projects/tsh'
        >>> with tsh.pushd("tsh"):
        ...     print(tsh.cwd())
        ...
        /Users/alefnula/projects/tsh/tsh
        >>> tsh.cwd()
        '/Users/alefnula/projects/tsh'

        # If the director doesn't exist.

        >>> with tsh.pushd("foo", create=True):
        ...     print(tsh.cwd())
        ...     with tsh.pushd("bar", create=True):
        ...         print(tsh.cwd())
        ...         with tsh.pushd("baz", create=True):
        ...             print(tsh.cwd())
        ...         print(tsh.cwd())
        ...     print(tsh.cwd())
        ...
        /Users/alefnula/projects/tsh/foo
        /Users/alefnula/projects/tsh/foo/bar
        /Users/alefnula/projects/tsh/foo/bar/baz
        /Users/alefnula/projects/tsh/foo/bar
        /Users/alefnula/projects/tsh/foo
        >>> tsh.cwd()
        '/Users/alefnula/projects/tsh'


    `pushd` is thread-safe in a very basic way: Only one thread can use it at
    a time. This means that if one thread is using re-entrant calls to `pushd`
    all other threads will have to wait for that thread to exit the last
    `with` statement so they can get hold of the re-entrant `pushd` lock.

    Since the application can only have one current working directory, this is
    the only way to achieve thread safety.
    ```

    """

    cwd = os.getcwd()
    path = os.path.abspath(path)

    # If create is True, create the directory if it doesn't exist.
    if create:
        os.makedirs(path, exist_ok=True)

    logger.debug("pushd -> %s", path)
    os.chdir(path)
    try:
        yield
    finally:
        logger.debug("pushd <- %s", path)
        os.chdir(cwd)
