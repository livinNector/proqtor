import os
from typing import Literal

from termcolor import colored, cprint

from proq.core import ProQ
from proq.evaluate_utils import (
    ProqCheck,
    TestCaseResult,
    get_test_case_results,
)
from proq.execute_utils import BuildFailedError

from .utils import color_diff


def print_failed_test_cases(
    test_case_results: list[TestCaseResult],
    test_case_type: Literal["public", "private"] = "private",
    diff_mode=False,
):
    test_case_type = test_case_type.title()
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


def evaluate_proq(proq: ProQ, verbose=False, diff_mode=False) -> ProqCheck:
    source_filename = proq.solution.execute_config.source_filename
    build_command = proq.solution.execute_config.build
    run_command = proq.solution.execute_config.run
    n_public = len(proq.public_testcases)
    n_private = len(proq.private_testcases)

    if verbose:
        print("Title:", colored(proq.title, "cyan", attrs=["bold"]))

    # Test solution with public and private test cases
    try:
        test_case_results = get_test_case_results(
            proq.solution.solution_code,
            proq.public_test_cases + proq.private_test_cases,
            source_filename=source_filename,
            run_command=run_command,
            build_command=build_command,
        )
    except BuildFailedError as e:
        if verbose:
            cprint("Build Failed", color="red", attrs=["bold"])
            cprint(e.build_output, color="red")
        return ProqCheck(solution_check=False, template_check=False)

    if verbose:
        public_passed = count_passed(test_case_results[:n_public])
        if public_passed < n_public:
            cprint("Public Test Cases:", attrs=["bold"])
            print_failed_test_cases(
                test_case_results[:n_public],
                test_case_type="public",
                diff_mode=diff_mode,
            )
        private_passed = count_passed(test_case_results[n_public:])
        if private_passed < n_private:
            cprint("Private Test Cases:", attrs=["bold"])
            print_failed_test_cases(
                test_case_results[n_public:],
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

    if not all(map(lambda x: x.passed, test_case_results)):
        return ProqCheck(solution_check=False, template_check=False)

    # Test template with public and private test cases
    try:
        template_test_case_results = get_test_case_results(
            proq.solution.template_code,
            proq.public_test_cases + proq.private_test_cases,
            source_filename=source_filename,
            run_command=run_command,
            build_command=build_command,
        )
    except BuildFailedError:
        if verbose:
            print(
                colored("Template Check:", attrs=["bold"]),
                colored("passed - build failed", color="green"),
            )
        return ProqCheck(solution_check=True, template_check=True)

    template_passed = any(result.passed for result in template_test_case_results)
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
                f"{count_passed(template_test_case_results[:n_public])}/{n_public} "
                "passed",
                "red",
                end="\t",
            )
            cprint(
                "private testcases: "
                f"{count_passed(template_test_case_results[n_public:])}/{n_private} "
                "passed",
                "red",
            )

    return proq_check


def evaluate_proq_files(*files: str | os.PathLike, verbose=False, diff_mode=False):
    """Evaluates the testcases in the proq files locally.

    It uses the local installed compilers and interpreters
    to evalate the testcases.

    The config on how to execute the solution code is present
    in the first line of the code block in the solution.

    ```{lang_id} {filename} -r '{run_command}' -b '{build_command}'

    Args:
        files (str|PathLike): The file names of the proqs to be evaluated.
        verbose (bool): Whether to print the test results.
        diff_mode (bool):
            Whether to display expected-actual diff instead of separate
            expected and actual outputs
    """
    proq_checks: list[tuple[str, ProqCheck]] = []
    for file_path in files:
        if not os.path.isfile(file_path):
            print(f"{file_path} is not a valid file")
            continue
        print(f"Evaluating {file_path}")
        proq = ProQ.from_file(file_path)
        result = evaluate_proq(proq, verbose=verbose, diff_mode=diff_mode)
        if verbose:
            print()
        proq_checks.append((file_path, result))

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
