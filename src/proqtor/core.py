import os
import re
import shutil
import subprocess
import warnings
from typing import Generic, Self, TypeVar

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator
from termcolor import colored, cprint
from unidecode import unidecode

import md2json

from .core_components import Solution, TestCase
from .evaluate_utils import (
    BuildFailedError,
    ProqCheck,
    code_run_env,
    get_test_case_results,
    print_solution_check_results,
    print_template_check_results,
)
from .execute_utils import get_command_output
from .parse import extract_solution, extract_testcases
from .prog_langs import ProgLang
from .template_utils import get_relative_env, package_env

PROBLEM_STATEMENT = "Problem Statement"
PUBLIC_TEST_CASES = "Public Test Cases"
PRIVATE_TEST_CASES = "Private Test Cases"
SOLUTION = "Solution"


class ProqParseError(Exception):
    def __init__(self, message, content):
        super().__init__(message)
        self.message = message
        self.content = content


class FrontMatter(BaseModel):
    title: str | None = None
    tags: list[str] | None = None
    model_config = ConfigDict(extra="allow")


class ProQ(BaseModel):
    """Pydantic model for a Programming Question (ProQ)."""

    title: str | None = Field(validation_alias="Title", description="Title")
    tags: list[str] | None = Field(
        default_factory=list,
        description="List of concept tags related to the programming question.",
    )

    statement: str = Field(
        validation_alias=PROBLEM_STATEMENT,
        description="The problem statement with example and explanation",
    )
    public_test_cases: list[TestCase] = Field(validation_alias=PUBLIC_TEST_CASES)
    private_test_cases: list[TestCase] = Field(validation_alias=PRIVATE_TEST_CASES)
    solution: Solution = Field(validation_alias=SOLUTION, description="The Solution")

    model_config = ConfigDict(
        validate_assignment=True, populate_by_name=True, extra="allow"
    )

    @property
    def public_testcases(self):
        warnings.warn(
            "public_testcases is deprecated, use public_test_cases instead",
            DeprecationWarning,
            stacklevel=2,
        )

        return self.public_test_cases

    @property
    def private_testcases(self):
        warnings.warn(
            "private_testcases is deprecated, use private_test_cases instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.private_test_cases

    @field_validator("title")
    @classmethod
    def remove_duplicates(cls, word):
        """Removes multiple spaces and strips whitespace in beginning and end."""
        return re.sub(re.compile(r"\s+"), " ", word).strip()

    @classmethod
    def default_proq(cls, lang: ProgLang = "python", n_public=1, n_private=1):
        return cls(
            title="Sample Title",
            tags=["sample tag 1", "sample tag 2"],
            statement="Sample Problem statment",
            public_test_cases=[TestCase(input="\n", output="\n")] * n_public,
            private_test_cases=[TestCase(input="\n", output="\n")] * n_private,
            solution=Solution.from_default(lang),
        )

    @classmethod
    def from_str(cls, content, base=None, render_template=False):
        if base is None:
            base = os.curdir
        try:
            yaml_header, md_string = content.split("---", 2)[1:]
        except Exception:
            raise ProqParseError(message="Yaml header not found.", content=content)
        try:
            yaml_header = yaml.safe_load(yaml_header)
        except Exception:
            raise ProqParseError(
                message="Invalid yaml in the yaml header", content=content
            )
        if "title" not in yaml_header:
            raise ProqParseError(
                message="Title not found in yaml header", content=content
            )

        try:
            env = get_relative_env(base)

            proq = {
                k.title(): env.from_string(v).render() if render_template else v
                for k, v in md2json.fold_level(md_string, level=1).items()
            }
        except Exception as e:
            raise ProqParseError(
                message="Error occured while parsing or rendering "
                f"first level header contents  - {e.__class__.__name__}: {e}",
                content=content,
            )

        missing_headings = []
        for heading in [
            PROBLEM_STATEMENT,
            SOLUTION,
            PUBLIC_TEST_CASES,
            PRIVATE_TEST_CASES,
        ]:
            if heading not in proq:
                missing_headings.append(heading)
        if missing_headings:
            many = len(missing_headings) > 1
            raise ProqParseError(
                message=f"The following required heading{'s' if many else ''} "
                f"{'are' if many else 'is'} missing - "
                + ((",".join(missing_headings[:-1]) + " and ") if many else "")
                + missing_headings[-1],
                content=content,
            )

        proq[PROBLEM_STATEMENT] = proq[PROBLEM_STATEMENT].strip()
        try:
            proq[SOLUTION] = extract_solution(proq[SOLUTION])
        except Exception as e:
            raise ProqParseError(
                message="Error occured while extracting solution"
                f" - {e.__class__.__name__}: {e}",
                content=content,
            )

        try:
            proq[PUBLIC_TEST_CASES] = md2json.fold_level(
                proq[PUBLIC_TEST_CASES], level=2, return_type="list"
            )
            proq[PUBLIC_TEST_CASES] = extract_testcases(proq[PUBLIC_TEST_CASES])
        except Exception as e:
            raise ProqParseError(
                message="Error occured while extracting public test cases"
                f" - {e.__class__.__name__}: {e}",
                content=content,
            )

        try:
            proq[PRIVATE_TEST_CASES] = md2json.fold_level(
                proq[PRIVATE_TEST_CASES], level=2, return_type="list"
            )
            proq[PRIVATE_TEST_CASES] = extract_testcases(proq[PRIVATE_TEST_CASES])
        except Exception as e:
            raise ProqParseError(
                message="Error occured while extracting public test cases"
                f" - {e.__class__.__name__}: {e}",
                content=content,
            )

        proq.update(yaml_header)
        return cls.model_validate(proq)

    @classmethod
    def from_file(cls, proq_file, render_template=True):
        """Loads the proq file and returns a Proq."""
        if not os.path.isfile(proq_file):
            raise FileNotFoundError(f"File {proq_file} does not exists.")
        with open(proq_file) as f:
            return ProQ.from_str(
                f.read(), os.path.dirname(proq_file), render_template=render_template
            )

    @property
    def front_matter(self):
        return FrontMatter(
            title=self.title,
            tags=self.tags,
            **self.model_extra,
        )

    def to_str(self, asciify=False) -> str:
        output = package_env.get_template("proq_template.md.jinja").render(proq=self)
        if asciify:
            output = unidecode(output)
        return output

    def to_file(self, file_name, asciify=False) -> str:
        with open(file_name, "w") as f:
            f.write(self.to_str(asciify=asciify))

    def get_test_case_results(self, code, test_cases):
        execute_config = self.solution.execute_config
        return get_test_case_results(
            code,
            test_cases,
            execute_config.source_filename,
            execute_config.run,
            execute_config.build,
        )

    def run(self):
        """Executes the code as it is run from the command line."""
        with code_run_env(
            self.solution.solution_code, self.solution.execute_config.source_filename
        ):
            if self.solution.execute_config.build:
                get_command_output(
                    self.solution.execute_config.build, raise_on_fail=True
                )

            return subprocess.run(self.solution.execute_config.run.split())

    def evaluate(self, verbose=False, diff_mode=False) -> ProqCheck:
        n_public = len(self.public_testcases)

        if verbose:
            print("Title:", colored(self.title, "cyan", attrs=["bold"]))

        # Test solution with public and private test cases
        try:
            test_case_results = self.get_test_case_results(
                self.solution.solution_code,
                self.public_test_cases + self.private_test_cases,
            )
        except BuildFailedError as e:
            if verbose:
                cprint("Build Failed", color="red", attrs=["bold"])
                cprint(e.command_output, color="red")
            return ProqCheck(solution_check=False, template_check=False)

        if verbose:
            print_solution_check_results(
                test_case_results[:n_public],
                test_case_results[n_public:],
                diff_mode=diff_mode,
            )

        if not all(map(lambda x: x.passed, test_case_results)):
            return ProqCheck(solution_check=False, template_check=False)

        if not re.match(r".*<sol>.*</sol>.*", self.solution.tagged_template, re.DOTALL):
            print(
                colored("Template Check:", attrs=["bold"]),
                colored(
                    "failed - No sol tag present in the template. "
                    "Atleast one sol tag must be present in the template.",
                    color="red",
                ),
            )
            return ProqCheck(solution_check=True, template_check=False)
        # Test template with public and private test cases
        try:
            template_test_case_results = self.get_test_case_results(
                self.solution.template_code,
                self.public_test_cases + self.private_test_cases,
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
            print_template_check_results(
                template_test_case_results[:n_public],
                template_test_case_results[n_public:],
                proq_check.template_check,
            )

        return proq_check

    def correct_outputs(self, inplace=False) -> Self:
        if not inplace:
            proq = self.model_copy(deep=True)
        else:
            proq = self
        test_cases = proq.public_test_cases + proq.private_test_cases
        test_case_results = self.get_test_case_results(
            self.solution.solution_code, test_cases
        )
        for test_case, test_case_result in zip(test_cases, test_case_results):
            test_case.output = test_case_result.actual_output
        return proq

    def export_test_cases(self, output_dir, zip=False):
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir()
        for test_case_set, set_name in [
            (self.public_test_cases, "public"),
            (self.private_test_cases, "private"),
        ]:
            curr_folder = output_dir / set_name
            (curr_folder).mkdir()
            for i, test_case in enumerate(test_case_set, 1):
                with open(curr_folder / f"input_{i:03}.txt", "w") as f:
                    f.write(test_case.input)
                with open(curr_folder / f"output_{i:03}.txt", "w") as f:
                    f.write(test_case.output)
        if zip:
            shutil.make_archive(output_dir, "zip", output_dir)
            shutil.rmtree(output_dir)


DataT = TypeVar("DataT")


class NestedContent(BaseModel, Generic[DataT]):
    title: str
    content: list["NestedContent[DataT]"] | DataT


def load_nested_proq_from_file(yaml_file) -> NestedContent[ProQ]:
    """Loads a nested content structure with proqs at leaf nodes."""
    with open(yaml_file) as f:
        nested_proq_files = NestedContent[str | ProQ].model_validate(yaml.safe_load(f))

    def load_nested_proq_files(nested_proq_files: NestedContent[str]):
        """Loads the nested Proqs inplace recursively."""
        if isinstance(nested_proq_files.content, str):
            nested_proq_files.content = ProQ.from_file(
                os.path.join(
                    os.path.dirname(os.path.abspath(yaml_file)),
                    nested_proq_files.content,
                )
            )
        else:
            for content in nested_proq_files.content:
                load_nested_proq_files(content)

    load_nested_proq_files(nested_proq_files)
    return NestedContent[ProQ].model_validate(nested_proq_files.model_dump())
