import os
import re
import warnings
from typing import Generic, TypeVar

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

import md2json

from .core_components import Solution, TestCase
from .lang_defaults import default_execute_config, default_solution
from .parse import extract_solution, extract_testcases
from .prog_langs import ProgLang
from .template_utils import get_relative_env, package_env

PROBLEM_STATEMENT = "Problem Statement"
PUBLIC_TEST_CASES = "Public Test Cases"
PRIVATE_TEST_CASES = "Private Test Cases"
SOLUTION = "Solution"


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
            DeprecationWarning,stacklevel=2
        )

        return self.public_test_cases

    @property
    def private_testcases(self):
        warnings.warn(
            "private_testcases is deprecated, use private_test_cases instead",
            DeprecationWarning,stacklevel=2
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
            statement="Sample Problem statment",
            public_test_cases=[TestCase(input="\n", output="\n")] * n_public,
            private_test_cases=[TestCase(input="\n", output="\n")] * n_private,
            solution=Solution(
                solution=default_solution[lang],
                template=default_solution[lang],
                lang=lang,
                execute_config=default_execute_config[lang],
            ),
        )

    @classmethod
    def from_file(cls, proq_file):
        """Loads the proq file and returns a Proq."""
        if not os.path.isfile(proq_file):
            raise FileNotFoundError(f"File {proq_file} does not exists.")

        with open(proq_file) as f:
            md_file = f.read()
        yaml_header, md_string = md_file.split("---", 2)[1:]
        yaml_header = yaml.safe_load(yaml_header)
        is_rendered = yaml_header.pop("is_rendered", False)

        if not is_rendered:
            env = get_relative_env(proq_file)
            md_string = env.from_string(md_string).render()
        proq = {k.title(): v for k, v in md2json.fold_level(md_string, level=1).items()}

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
            raise ValueError(
                f"The following required heading{'s' if many else ''} "
                f"{'are' if many else 'is'} missing - "
                + ((",".join(missing_headings[:-1]) + " and ") if many else "")
                + missing_headings[-1],
            )

        proq[PUBLIC_TEST_CASES] = md2json.fold_level(
            proq[PUBLIC_TEST_CASES], level=2, return_type="list"
        )
        proq[PRIVATE_TEST_CASES] = md2json.fold_level(
            proq[PRIVATE_TEST_CASES], level=2, return_type="list"
        )
        proq[PROBLEM_STATEMENT] = proq[PROBLEM_STATEMENT].strip()
        proq[SOLUTION] = extract_solution(proq[SOLUTION])
        proq[PUBLIC_TEST_CASES] = extract_testcases(proq[PUBLIC_TEST_CASES])
        proq[PRIVATE_TEST_CASES] = extract_testcases(proq[PRIVATE_TEST_CASES])
        proq.update(yaml_header)
        return cls.model_validate(proq)

    def to_file(self, file_name):
        template = package_env.get_template("proq_template.md.jinja")
        with open(file_name, "w") as f:
            f.write(template.render(proq=self))


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
