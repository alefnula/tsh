import os
import shutil
from typing import Optional, List
from tsh.types import Path
from tsh.process import Process
from tsh.errors import CommandNotFound


class Command:
    """Command represents a blueprint of a command run.

    Options:
        _fg: Run command in foreground.
        _in: Redirect stdin stream.
        _out: Redirect stdout stream.
        _err: Redirect stderr stream.
        _kwargs_sep: When using kwargs to bake a command, the separator is
            used as a delimiter between a kwargs key and value.
            Default: ` ` (Other value can be `=`).
            `=`.
        _kwargs_prefix: Prefix used for baked kwargs. Default: `--`.
            This means that if we bake a command with `foo=bar`, the
            command will be called with `--foo bar` arguments. Setting the
            `_kwargs_sep` to `=` will produce `--foo=bar` argument.
    """

    DEFAULT_OPTIONS = {
        "fg": False,
        "in": None,
        "out": None,
        "err": None,
        "kwargs_sep": " ",
        "kwargs_prefix": "--",
    }

    def __init__(
        self, command: str, search_paths: Optional[List[Path]] = None
    ):
        path = (
            None
            if search_paths is None
            else os.pathsep.join(map(str, search_paths))
        )
        found = shutil.which(cmd=command, path=path)
        if found is None:
            raise CommandNotFound(command)

        self.command = found
        self.search_paths = search_paths
        self._options = self.DEFAULT_OPTIONS.copy()
        self._args = []
        self._kwargs = {}

    def bake(self, *args, **kwargs) -> "Command":
        """Bake arguments and options.

        Returns:
            A new instance of a Command with baked args.
        """
        cmd = Command(command=self.command, search_paths=self.search_paths)

        # Set baked args
        cmd._args = self._args.copy() + list(args)

        # Filter out options from kwargs and remove them
        options = {}
        for option in self.DEFAULT_OPTIONS:
            key = f"_{option}"
            if key in kwargs:
                options[option] = kwargs.pop(key)

        # Set baked kwargs
        cmd._kwargs = {**self._kwargs, **kwargs}

        # Set baked options
        cmd._options = {**self._options, **options}

        return cmd

    @property
    def command_list(self) -> List[str]:
        """Return a command as a list.

        This is used when launching a process and as an intermediary
        representation for creating `command_line`.
        """
        command = [self.command, *self._args]
        sep = self._options["kwargs_sep"]
        prefix = self._options["kwargs_prefix"]

        for key, value in self._kwargs.items():
            if sep == " ":
                command.extend([f"{prefix}{key}", value])
            else:
                command.append(f"{prefix}{key}{sep}{value}")

        return command

    @property
    def command_line(self) -> str:
        """Return the command line that will be executed."""
        return " ".join(
            [
                f'"{item}"' if " " in item else item
                for item in self.command_list
            ]
        )

    def __call__(self, *args, **kwargs) -> Process:
        c = self.bake(*args, **kwargs)
        p = Process(command=c.command_list)
        p.start()
        return p

    def __str__(self):
        return self.command_line

    __repr__ = __str__
