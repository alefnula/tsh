import os
import logging
from tsh.types import Path


logger = logging.getLogger(__name__)


def cwd() -> str:
    """Return the absolute path to the current working directory."""
    return os.path.abspath(os.getcwd())


def cd(path: Path, create: bool = False):
    """Change directory.

    Args:
        path: Path to the directory we want to enter.
        create: Create the directory if it doesn't exist.
    """
    if create:
        os.makedirs(path, exist_ok=True)

    logger.debug("cd -> %s", path)
    os.chdir(str(path))
