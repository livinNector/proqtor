import os
import subprocess
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from tempfile import TemporaryDirectory

from termcolor import colored, cprint

from .core import ProQ, TestCase

ProqCheck = namedtuple("ProqCheck", ["solution_check", "template_check"])

TestCaseResult = namedtuple(
    "TestCaseResult", ["input", "expected_output", "actual_output", "passed"]
)


def write_to_file(content, file_name):
    with open(file_name, "w") as f:
        f.write(content)


def build(build_command) -> tuple[bool, str]:
    """Builds with the given build command.

    Args:
        build_command : str - build command to run in a subprocess

    Return:
        status: bool - True if build succeeds, False otherwise
        output: str - The output of build command

    """
    result = subprocess.run(
        build_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    return (result.returncode == 0, result.stderr + result.stdout)


def get_output(command: str, stdin: str):
    result = subprocess.run(
        command.split(),
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return result.stdout


def check_testcases(
    run_command: str,
    testcases: list[TestCase],
):
    with ThreadPoolExecutor(max_workers=len(testcases)) as executor:
        actual_outputs = executor.map(
            get_output,
            repeat(run_command, len(testcases)),
            [testcase.input for testcase in testcases],
        )
    results = []
    for actual_output, testcase in zip(actual_outputs, testcases):
        actual_output = actual_output.strip().replace("\r", "")
        expected_output = testcase.output.strip().replace("\r", "")
        passed = actual_output == expected_output
        results.append(
            TestCaseResult(testcase.input, expected_output, actual_output, passed)
        )
    return results


def print_failed_testcases(testcase_results):
    for i, result in enumerate(testcase_results, 1):
        if not result.passed:
            cprint(f"Test case {i}: Failed", "red", attrs=["bold"])
            cprint("Input:", attrs=["bold"])
            print(result.input.strip())
            cprint("Expected output:", attrs=["bold"])
            print(result.expected_output)
            cprint("Actual output:", attrs=["bold"])
            print(result.actual_output or "{{NO OUPUT}}")


def count_passed(results):
    return sum(map(lambda x: x.passed, results))


def evaluate_proq(proq: ProQ, verbose=False) -> ProqCheck:
    source_filename = proq.solution.execute_config.source_filename
    build_command = proq.solution.execute_config.build
    run_command = proq.solution.execute_config.run
    n_public = len(proq.public_testcases)
    n_private = len(proq.private_testcases)

    if verbose:
        print("Title:", colored(proq.title, attrs=["bold"]))

    # Write solution code and build
    write_to_file(proq.solution.solution_code, source_filename)
    if build_command:
        result, output = build(build_command)
        if not result:
            if verbose:
                cprint("Build Failed", color="red", attrs=["bold"])
                cprint(output, color="red")
            return ProqCheck(solution_check=False, template_check=False)

    # Test solution with public and private test cases
    testcase_results = check_testcases(
        run_command, proq.public_testcases + proq.private_testcases
    )
    if verbose:
        public_passed = count_passed(testcase_results[:n_public])
        if public_passed < n_public:
            cprint("Public Test Cases:", attrs=["bold"])
            print_failed_testcases(testcase_results[:n_public])
        private_passed = count_passed(testcase_results[n_public:])
        if private_passed < n_private:
            cprint("Private Test Cases:", attrs=["bold"])
            print_failed_testcases(testcase_results[n_public:])
        cprint("Solution check: ", attrs=["bold"], end="")
        cprint(
            f"{public_passed}/{n_public} public test cases passed",
            "red" if public_passed < n_public else "green",
            end="\t",
        )
        cprint(
            f"{private_passed}/{n_private} private test cases passed",
            "red" if private_passed < n_private else "green",
        )

    if not all(map(lambda x: x.passed, testcase_results)):
        return ProqCheck(solution_check=False, template_check=False)

    # Write template code and build
    write_to_file(proq.solution.template_code, source_filename)
    if build_command:
        result, output = build(build_command)
        if not result:
            if verbose:
                print(
                    colored("Template check:", attrs=["bold"]),
                    colored("passed - build failed", color="green"),
                )
            return ProqCheck(solution_check=True, template_check=True)

    # Test template with public and private test cases
    template_testcase_results = check_testcases(
        run_command, proq.public_testcases + proq.private_testcases
    )

    template_passed = any(result.passed for result in template_testcase_results)
    proq_check = ProqCheck(solution_check=True, template_check=not template_passed)

    if verbose:
        status = (
            colored("passed", color="green")
            if proq_check.template_check
            else colored("failed", color="red")
        )
        print(
            colored("Template check: ", attrs=["bold"]),
            status,
            end=" | " if not proq_check.template_check else "\n",
        )
        if not proq_check.template_check:
            cprint(
                "public testcases: "
                f"{count_passed(template_testcase_results[:n_public])}/{n_public} "
                "passed",
                "red",
                end="\t",
            )
            cprint(
                "private testcases: "
                f"{count_passed(template_testcase_results[n_public:])}/{n_private} "
                "passed",
                "red",
            )

    return proq_check


def evaluate_proq_files(*files: str | os.PathLike, verbose=False):
    """Evaluates the testcases in the proq files locally.

    It uses the local installed compilers and interpreters
    to evalate the testcases.

    The config on how to execute the solution code is present
    in the first line of the code block in the solution.

    ```{lang_id} {filename} -r '{run_command}' -b '{build_command}'

    Args:
        files (str|PathLike): The file names of the proqs to be evaluated.
        verbose (bool): Whether to print the test results.
    """
    proq_checks: list[tuple[str, ProqCheck]] = []
    for file_path in files:
        if not os.path.isfile(file_path):
            print(f"{file_path} is not a valid file")
            continue
        # if verbose:
        print(f"Evaluating file {file_path}")
        proq = ProQ.from_file(file_path)
        curdir = os.path.abspath(os.curdir)
        with TemporaryDirectory() as tempdirname:
            os.chdir(tempdirname)
            result = evaluate_proq(proq, verbose=verbose)
            if verbose:
                print()
            proq_checks.append((file_path, result))
            os.chdir(curdir)

    n_proqs = len(proq_checks)
    cprint(
        f"Total of {n_proqs} proq{'s' if n_proqs>1 else ''} evaluated.", attrs=["bold"]
    )
    for file_path, proq_check in proq_checks:
        cprint(
            ("✓" if proq_check.solution_check else "✗") + " solution",
            "green" if proq_check.solution_check else "red",
            end=" ",
        )
        cprint(
            ("✓" if proq_check.template_check else "✗") + " template",
            "green" if proq_check.template_check else "red",
            end=" ",
        )
        print(os.path.relpath(file_path, os.curdir))
