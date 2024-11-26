import argparse
import os
import subprocess
from collections import namedtuple
from tempfile import TemporaryDirectory

from termcolor import colored, cprint

from .core import ProQ, TestCase

ProqChecks = namedtuple("ProqChecks", ["solution_checks", "template_checks"])


def write_to_file(content, file_name):
    with open(file_name, "w") as f:
        f.write(content)


def build(build_command) -> tuple[bool,str]:
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
    return (result.returncode == 0, result.stderr+result.stdout)


def run_script(run_command: str, stdin: str):
    result = subprocess.run(
        run_command.split(),
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return result.stdout


def check_testcases(run_command: str, testcases: list[TestCase], verbose=False):
    results = []
    for i, testcase in enumerate(testcases, 1):
        actual_output = (
            run_script(run_command, testcase.input).strip().replace("\r", "")
        )
        expected_output = testcase.output.strip()
        passed = actual_output == expected_output
        results.append(passed)

        if verbose:
            cprint(
                f"Test case {i}: Passed" if passed else f"Test case {i}: Failed",
                color="green" if passed else "red",
            )
            if not passed:
                print(
                    "Input:",
                    testcase.input,
                    "Expected output:",
                    expected_output,
                    "Actual output:",
                    actual_output,
                    sep="\n",
                )
    return results


def evaluate_proq(proq: ProQ, verbose=False) -> dict[str, ProqChecks]:
    source_filename = proq.solution.execute_config.source_filename
    build_command = proq.solution.execute_config.build
    run_command = proq.solution.execute_config.run

    if verbose:
        print("Title:", colored(proq.title, attrs=["bold"]))

    # Write solution code and build
    write_to_file(proq.solution.solution_code, source_filename)
    if build_command:
        result, output = build(build_command)
        if not result:
            if verbose:
                cprint("Build Failed", color="red", attrs=["bold"])
                cprint(output, color='red')
            return ProqChecks(solution_checks=False, template_checks=False)

    # Test solution with public and private test cases
    if verbose:
        cprint("Public Testcases", attrs=["bold"])
    public_results = check_testcases(run_command, proq.public_testcases, verbose)

    if verbose:
        cprint("Private Testcases", attrs=["bold"])
    private_results = check_testcases(run_command, proq.private_testcases, verbose)

    if not all(public_results + private_results):
        return ProqChecks(solution_checks=False, template_checks=False)

    # Write template code and build
    write_to_file(proq.solution.template_code, source_filename)
    if build_command:
        result, output = build(build_command)
        if not result:
            if verbose:
                print("Template:", colored("Build Failed", color="green"))
            return ProqChecks(solution_checks=True, template_checks=True)

    # Test template with public and private test cases
    template_public_results = check_testcases(run_command, proq.public_testcases)
    template_private_results = check_testcases(run_command, proq.private_testcases)

    template_passed = any(template_public_results + template_private_results)

    proq_check = ProqChecks(solution_checks=True, template_checks=not template_passed)

    if verbose:
        status = (
            colored("Passed", color="green")
            if proq_check.template_checks
            else colored("Failed", color="red")
        )
        print(colored("Template Check:", attrs=["bold"]), status)
        if not proq_check.template_checks:
            print(f"Public Testcases: {sum(template_public_results)} Passed")
            print(f"Private Testcases: {sum(template_private_results)} Passed")

    return proq_check


def evaluate_proq_files(files, verbose=True):
    for file_path in files:
        if not os.path.isfile(file_path):
            print(f"{file_path} is not a valid file")
            continue
        print(f"Evaluating file {file_path}")
        proq = ProQ.from_file(file_path)
        curdir = os.path.abspath(os.curdir)
        with TemporaryDirectory() as tempdirname:
            os.chdir(tempdirname)
            evaluate_proq(proq, verbose=verbose)
            os.chdir(curdir)


def configure_cli_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "files", metavar="F", type=str, nargs="+", help="proq files to be evaluated"
    )
    parser.set_defaults(func=lambda args: evaluate_proq_files(args.files))
