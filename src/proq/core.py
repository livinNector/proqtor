import difflib
import os
import re
from typing import Generic, TypeVar

import yaml
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

import md2json

from .parse import extract_solution, extract_testcases
from .prog_langs import ProgLang
from .template_utils import get_relative_env


class TestCase(BaseModel):
    input: str
    output: str


class ExecuteConfig(BaseModel):
    source_filename: str | None = ""
    build: str | None = ""
    run: str | None = ""


class Solution(BaseModel):
    prefix: str = Field(default="", description="The prefix of the solution")
    template: str = Field(
        default="", description="Template code between prefix and suffix"
    )
    solution: str = Field(
        default="", description="The solution code to replace template"
    )
    suffix: str = Field(default="", description="The suffix of the solution")
    suffix_invisible: str = Field(
        default="",
        validation_alias=AliasChoices("suffix_invisible", "invisible_suffix"),
        description="The invisible part of the suffix that comes after suffix",
    )
    lang: ProgLang = Field(default="python")
    execute_config: ExecuteConfig | None = Field(default_factory=ExecuteConfig)

    @property
    def solution_code(self):
        """The complete solution code with all prefix and suffix attached."""
        return "".join([self.prefix, self.solution, self.suffix, self.suffix_invisible])

    @property
    def template_code(self):
        """The complete template code with all prefix and suffix attached."""
        return "".join([self.prefix, self.template, self.suffix, self.suffix_invisible])

    @property
    def template_solution_diff(self):
        differ = difflib.Differ()
        differences = differ.compare(
            self.template.splitlines(keepends=True),
            self.solution.splitlines(keepends=True),
        )
        return list(differences)


class ProQ(BaseModel):
    """Pydantic model for a Programming Question (ProQ)."""

    title: str | None = Field(validation_alias="Title", description="Title")
    tags: list[str] | None = Field(
        default_factory=list,
        description="List of concept tags related to the programming question.",
    )

    statement: str = Field(
        validation_alias="Problem Statement",
        description="The problem statement with example and explanation",
    )
    public_testcases: list[TestCase] = Field(validation_alias="Public Test Cases")
    private_testcases: list[TestCase] = Field(validation_alias="Private Test Cases")
    solution: Solution = Field(validation_alias="Solution", description="The solution")

    model_config = ConfigDict(
        validate_assignment=True, populate_by_name=True, extra="allow"
    )

    @field_validator("title")
    @classmethod
    def remove_duplicates(cls, word):
        """Removes multiple spaces and strips whitespace in beginning and end."""
        return re.sub(re.compile(r"\s+"), " ", word).strip()

    @classmethod
    def default_proq(cls):
        return cls(
            title="Sample Title",
            statement="Sample Problem statment",
            public_testcases=[TestCase(input="a", output="a")],
            private_testcases=[TestCase(input="a", output="a")],
            solution=Solution(
                solution="print(input())",
                lang="python",
            ),
        )

    @classmethod
    def from_file(cls, proq_file):
        """Loads the proq file and returns a Proq."""
        if not os.path.isfile(proq_file):
            raise FileNotFoundError(f"File {proq_file} does not exists.")

        md_file = (
            get_relative_env(proq_file)
            .get_template(os.path.basename(proq_file))
            .render()
        )
        yaml_header, md_string = md_file.split("---", 2)[1:]
        yaml_header = yaml.safe_load(yaml_header)
        proq = md2json.dictify(md_string)
        if isinstance(proq["Problem Statement"], dict):
            proq["Problem Statement"] = md2json.undictify(
                proq["Problem Statement"], level=2
            )

        proq["Solution"] = extract_solution(proq["Solution"])
        proq["Public Test Cases"] = extract_testcases(proq["Public Test Cases"])
        proq["Private Test Cases"] = extract_testcases(proq["Private Test Cases"])
        proq.update(yaml_header)
        return cls.model_validate(proq)


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
