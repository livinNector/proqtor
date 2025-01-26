import subprocess
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat


class BuildFailedError(Exception):
    """Raised when a build process fails.

    Attributes:
        build_output (str): Contains the output from the build process.
    """

    def __init__(self, build_output, *args):
        super().__init__(build_output, *args)
        self.build_output = build_output


def build(build_command) -> str:
    """Builds with the given build command.

    Args:
        build_command (str):  build command to run in a subprocess

    Return:
        output (str):  The output of build command

    Raises:
        BuildFailedError: if build process returns a non-zero
    """
    result = subprocess.run(
        build_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    build_output = result.stderr + result.stdout
    if result.returncode != 0:
        raise BuildFailedError(build_output=build_output)
    return build_output


def get_output(command: str, stdin: str):
    result = subprocess.run(
        command.split(),
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return result.stdout


def get_outputs(command, stdins: list[str]):
    n = len(stdins)
    with ThreadPoolExecutor(max_workers=n) as executor:
        return executor.map(
            get_output,
            repeat(command, n),
            stdins,
        )
