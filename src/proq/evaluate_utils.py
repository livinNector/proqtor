import os
import subprocess
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from tempfile import TemporaryDirectory

from .core_components import TestCase

ProqCheck = namedtuple("ProqCheck", ["solution_check", "template_check"])

TestCaseResult = namedtuple(
    "TestCaseResult", ["input", "expected_output", "actual_output", "passed"]
)


def write_to_file(content, file_name):
    with open(file_name, "w") as f:
        f.write(content)


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


def check_test_cases(
    run_command: str,
    test_cases: list[TestCase],
):
    with ThreadPoolExecutor(max_workers=len(test_cases)) as executor:
        actual_outputs = executor.map(
            get_output,
            repeat(run_command, len(test_cases)),
            [testcase.input for testcase in test_cases],
        )
    results = []
    for actual_output, testcase in zip(actual_outputs, test_cases):
        actual_output = actual_output.replace("\r", "")
        expected_output = testcase.output.replace("\r", "")
        passed = actual_output.strip() == expected_output.strip()
        results.append(
            TestCaseResult(testcase.input, expected_output, actual_output, passed)
        )
    return results


def get_test_case_results(
    code,
    test_cases,
    source_filename,
    run_command,
    build_command=None,
) -> list[TestCaseResult]:
    """Returns the test case results after evaluating the test cases.

    Args:
        code (str): The full code to execute.
        test_cases (list[TestCase]): The list of test cases.
        source_filename (str): The file name of the file to run.
        run_command (str): The command to run the code.
        build_command (str): The build command to build or compile the code.

    Returns:
        results (list[TestCaseResult]): The list of test case results.

    Raises:
        BuildFailedError:  if the build process fails.
    """
    curdir = os.path.abspath(os.curdir)
    with TemporaryDirectory() as tempdirname:
        os.chdir(tempdirname)
        try:
            write_to_file(code, source_filename)
            if build_command:
                build(build_command)
            return check_test_cases(run_command, test_cases)
        finally:
            os.chdir(curdir)
