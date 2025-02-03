import subprocess
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat


class CommandFailedError(Exception):
    """Raised when a command process fails.

    Attributes:
        command_output (str): contains the output from the command
    """

    def __init__(self, command_output, *args):
        super().__init__(command_output, *args)
        self.command_output = command_output


def get_command_output(command: str, stdin: str = "", raise_on_fail: bool = False):
    """Runs the given command and returns the output.

    Args:
        command (str):  build  to run in a subprocess
        stdin (str): the contents of the stdin passed
        raise_on_fail (bool): whether to raise an exception on non zero return status.

    Return:
        output (str):  The output of build command

    Raises:
        BuildFailedError: if build process returns a non-zero
    """
    result = subprocess.run(
        command.split(),
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    output = result.stderr + result.stdout
    if raise_on_fail and result.returncode != 0:
        raise CommandFailedError(command_output=output)
    return output


def get_outputs(command, stdins: list[str], raise_on_fail: bool = False):
    n = len(stdins)
    with ThreadPoolExecutor(max_workers=n) as executor:
        return executor.map(
            get_command_output, repeat(command, n), stdins, repeat(raise_on_fail, n)
        )
