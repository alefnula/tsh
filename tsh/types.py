import io
import pathlib
from dataclasses import dataclass
from typing import Union, Optional


# Path can either a string or a pathlib.Path object
Path = Union[str, pathlib.Path]

# IO can be either:
#   1. None          - In this case the IO object is closed
#   2. str           - String is interpreted as a path to a file that should be
#                      opened for read or write (whatever the IO requests).
#   3. bool          - False has same behaviour as None and True will redirect
#                      to a internal buffer.
#   4. io.TextIOBase - Open file object, StringIO, etc...
IO = Optional[Union[str, bool, io.TextIOBase]]


@dataclass
class Result:
    exit_code: int
    stdout: str
    stderr: str
