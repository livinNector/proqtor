import os
from collections import namedtuple
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from termcolor import colored, cprint

from .core_components import TestCase
from .execute_utils import CommandFailedError, get_command_output, get_outputs
from .utils import color_diff

ProqCheck = namedtuple("ProqCheck", ["solution_check", "template_check"])

TestCaseResult = namedtuple(
    "TestCaseResult", ["input", "expected_output", "actual_output", "passed"]
)


class BuildFailedError(CommandFailedError):
    pass


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


@contextmanager
def code_run_env(code, source_filename):
    """Writes the code in the source file in a tempdir and changes to that dir.

    Args:
        code (str): The source code toe be written.
        source_filename (str): The filename to use to write the source code.
    """
    curdir = os.path.abspath(os.curdir)
    with TemporaryDirectory() as tempdirname:
        os.chdir(tempdirname)
        try:
            Path(source_filename).write_text(code)
            yield
        except CommandFailedError as e:
            raise BuildFailedError(e.command_output)
        finally:
            os.chdir(curdir)


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
    with code_run_env(code, source_filename=source_filename):
        if build_command:
            get_command_output(build_command, raise_on_fail=True)
        return check_test_cases(run_command, test_cases)


def print_failed_test_cases(
    test_case_results: list[TestCaseResult],
    test_case_type: Literal["public", "private"] = "private",
    diff_mode=False,
):
    test_case_type = test_case_type.title()
    cprint(f"{test_case_type} Test Cases:", attrs=["bold"])
    for i, result in enumerate(test_case_results, 1):
        if not result.passed:
            cprint(f"{test_case_type} Test Case {i}: Failed", "red", attrs=["bold"])
            cprint("Input:", "cyan", attrs=["bold"])
            print(result.input.strip())
            if not diff_mode:
                cprint("Expected Output:", "cyan", attrs=["bold"])
                print(result.expected_output)
                cprint("Actual Output:", "cyan", attrs=["bold"])
                print(result.actual_output or "{{NO OUPUT}}")
            else:
                cprint("Expected - Actual Diff:", "cyan", attrs=["bold"])
                color_diff(result.expected_output, result.actual_output)
                print()


def count_passed(results: list[TestCaseResult]):
    return sum(map(lambda x: x.passed, results))


def get_passed(results: list[TestCaseResult]):
    return [i for i, result in enumerate(results, 1) if result.passed]


def print_solution_check_results(
    public_test_cases, private_test_cases, diff_mode=False
):
    n_public = len(public_test_cases)
    n_private = len(private_test_cases)
    public_passed = count_passed(public_test_cases)
    private_passed = count_passed(private_test_cases)
    if public_passed < n_public:
        print_failed_test_cases(
            public_test_cases,
            test_case_type="public",
            diff_mode=diff_mode,
        )
    if private_passed < n_private:
        print_failed_test_cases(
            private_test_cases,
            test_case_type="private",
            diff_mode=diff_mode,
        )
    cprint("Solution Check: ", attrs=["bold"], end="")
    cprint(
        f"{public_passed}/{n_public} public test cases passed",
        "red" if public_passed < n_public else "green",
        end="\t",
    )
    cprint(
        f"{private_passed}/{n_private} private test cases passed",
        "red" if private_passed < n_private else "green",
    )


def print_template_check_results(public_test_cases, private_test_cases, template_check):
    status = (
        colored("passed", color="green")
        if template_check
        else colored("failed", color="red")
    )
    print(
        colored("Template check: ", attrs=["bold"]),
        status,
        end=" | " if not template_check else "\n",
    )
    if not template_check:
        passed_test_cases = ",".join(map(str, get_passed(public_test_cases)))
        if passed_test_cases:
            cprint(
                f"public testcase: {passed_test_cases} passed",
                "red",
                end="\t",
            )
        passed_test_cases = ",".join(map(str, get_passed(private_test_cases)))
        if passed_test_cases:
            cprint(
                f"private testcase: {passed_test_cases} passed",
                "red",
            )
