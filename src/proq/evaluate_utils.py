import os
from collections import namedtuple
from pathlib import Path
from tempfile import TemporaryDirectory

from .core_components import TestCase
from .execute_utils import build, get_outputs

ProqCheck = namedtuple("ProqCheck", ["solution_check", "template_check"])

TestCaseResult = namedtuple(
    "TestCaseResult", ["input", "expected_output", "actual_output", "passed"]
)

def check_test_cases(
    run_command: str,
    test_cases: list[TestCase],
):
    actual_outputs = get_outputs(
        run_command, [test_case.input for test_case in test_cases]
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
            Path(source_filename).write_text(code)
            if build_command:
                build(build_command)
            return check_test_cases(run_command, test_cases)
        finally:
            os.chdir(curdir)
