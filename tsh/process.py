import io
import os
import time
import posix
import signal
import logging
import threading
import subprocess
from typing import Dict, List, Union, Optional
from tsh import consts
from tsh.types import IO, Result
from tsh.errors import CommandNotFound

logger = logging.getLogger(__name__)


class Process:
    """Process class."""

    def __str__(self):
        return f"Process(pid={self.pid}, command={self.command})"

    __repr__ = __str__

    @staticmethod
    def _create_env(env):
        full_env = {str(key): str(value) for key, value in os.environ.items()}
        if env is not None:
            full_env.update(
                {str(key): str(value) for key, value in env.items()}
            )
        return full_env

    def __init__(
        self,
        command: List[str],
        stdout: IO = None,
        stderr: IO = None,
        demux: bool = True,
        environment: Optional[Dict[str, str]] = None,
        working_dir: Optional[str] = None,
        encoding: str = consts.encoding,
    ):
        """Create a Process object.

        The only required parameter is the command to execute. It's important
        to note that the constructor only initializes the class, it doesn't
        executes the process. To actually execute the process you have to call
        :met:`start`.

        Args:
            command: Command with optional arguments.
            stdout: Path to the file to which standard output would be
                redirected.
            stderr: Path to the file to which standard error would be
                redirected.
            demux: Demux stdout and stderr. Default: True
            environment: Optional additional environment variables that will be
                added to the subprocess environment or that will override
                currently set environment variables.
            working_dir: Set the working directory from which the process will
                be started. Default: Current working dir.
            encoding: Process stdin, stdout and stderr encoding.
        """
        self._command = command
        self._process = None
        self._wait_thread = None
        self._stdout = None if stdout is None else os.path.abspath(stdout)
        self._stderr = None if stderr is None else os.path.abspath(stderr)
        self._demux = demux
        self._stdout_writer = None
        self._stderr_writer = None
        self._working_dir = working_dir or os.getcwd()
        self._environment = environment
        self.encoding = encoding

    @property
    def command(self):
        """Command."""
        return self._command[0]

    @property
    def arguments(self):
        """Arguments."""
        return self._command[1:]

    def __process_wait(self):
        self._process.wait()
        if self._stdout_writer != subprocess.PIPE:
            self._stdout_writer.close()
        if self._stderr_writer != subprocess.PIPE and self._demux:
            self._stderr_writer.close()

    def start(self):
        """Start the process."""
        # Setup stdout
        self._stdout_writer = (
            subprocess.PIPE
            if self._stdout is None
            else io.open(self._stdout, "wb")
        )

        # Setup stderr
        if self._demux:
            self._stderr_writer = (
                subprocess.PIPE
                if self._stderr is None
                else io.open(self._stderr, "wb")
            )
        else:
            self._stderr_writer = self._stderr_writer

        try:
            self._process = subprocess.Popen(
                self._command,
                stdin=subprocess.PIPE,
                stdout=self._stdout_writer,
                stderr=self._stderr_writer,
                env=self._create_env(self._environment),
                cwd=self._working_dir,
            )
        except OSError:
            raise CommandNotFound(
                'Executable "{}" not found'.format(self.command)
            )
        self._wait_thread = threading.Thread(
            target=self.__process_wait, daemon=True
        )
        self._wait_thread.start()

    def kill(self) -> Optional[bool]:
        """Kill the process if it's running.

        Returns:
            True if the process is killed, False if an error happened or None
            if the process is not running.
        """
        try:
            if self._process is not None:
                self._process.kill()
                self.wait(0.5)
                if self.is_running:
                    if self.pid == posix.getpgid(self.pid):
                        os.killpg(self.pid, signal.SIGKILL)
                    else:
                        os.kill(self.pid, signal.SIGKILL)
                self._wait_thread.join()
                self._process = None
                return True
            else:
                return None
        except OSError:
            return False

    def wait(self, timeout=None) -> bool:
        """Wait for the process to finish.

        It will wait for the process to finish running. If the timeout is
        provided, the function will wait only ``timeout`` amount of seconds and
        then return to it's caller.

        Args:
            timeout (int, optional): ``None`` if you want to wait to wait until
                the process actually finishes, otherwise it will wait just the
                ``timeout`` number of seconds.

        Returns:
            bool: Return value only makes sense if you provided the timeout
                parameter. It will indicate if the process actually finished in
                the amount of time specified, i.e. if the we specify 3 seconds
                and the process actually stopped after 3 seconds it will return
                ``True`` otherwise it will return ``False``.
        """
        if timeout is not None:
            current_time = time.time()
            while time.time() - current_time < (timeout * 1000):
                if not self.is_running:
                    return True
                time.sleep(0.1)
            return False
        else:
            while self.is_running:
                time.sleep(0.1)
            return True

    @property
    def is_running(self) -> bool:
        """Indicate if the process is still running.

        Returns:
            bool: ``True`` if the process is still running ``False`` otherwise.
        """
        if self._process is None or self._process.returncode is not None:
            return False
        return True

    @property
    def pid(self) -> Optional[int]:
        """PID of the process if it is running.

        Returns:
            int or None: Process id of the running process.
        """
        if self.is_running:
            return self._process.pid
        return None

    @property
    def exit_code(self) -> Optional[int]:
        """Exit code if the process has finished running.

        Returns:
            int or None: Exit code or ``None`` if the process is still running.
        """
        if self.is_running:
            return None
        return self._process.returncode

    def write(self, string: str):
        """Write a string to the process standard input.

        Args:
            string (str): String to write to the process standard input.
        """
        if string[-1] != "\n":
            string += "\n"
        self._process.stdin.write(string.encode(self.encoding))
        self._process.stdin.flush()

    def read(self) -> str:
        """Read from the process standard output.

        Returns:
            The data process has written to the standard output if it has
            written anything. If it hasn't or you already read all the data
            process wrote, it will return an empty string.
        """
        if self._stdout is None:
            return self._process.stdout.read().decode(self.encoding)
        else:
            with io.open(self._stdout, "r", encoding=self.encoding) as f:
                return f.read()

    def eread(self) -> str:
        """Read from the process standard error.

        Returns:
            The data process has written to the standard error if it has
            written anything. If it hasn't or you already read all the data
            process wrote, it will return an empty string.
        """
        if self._demux:
            if self._stderr is None:
                return self._process.stderr.read().decode(self.encoding)
            else:
                with io.open(self._stderr, "r", encoding=self.encoding) as f:
                    return f.read()
        else:
            return ""


def execute(
    command: Union[str, List[str]],
    demux: bool = True,
    environment: dict = None,
    working_dir: str = None,
) -> Result:
    """Execute a command and return the exit code, stdout and stderr.

    Args:
        command: Command to execute.
        demux: Demux stdout and stderr.
        environment: Environment variables.
        working_dir: Set the working dir.

    Returns:
        Tuple (exit_code, stdout, stderr).
    """
    p = Process(
        command=command,
        demux=demux,
        environment=environment,
        working_dir=working_dir,
    )
    p.start()
    p.wait()
    return Result(p.exit_code, p.read(), p.eread())
