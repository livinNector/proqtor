from pydantic import (
    BaseModel,
    Field,
    computed_field,
    AliasChoices,
    field_validator,
)
from typing import Literal
import re

ProgLang = Literal[
    "c", "cpp", "java", "py", "py3", "verilog", "pl", "hs", "zip", "bash", "javascript"
]


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
        validation_alias=AliasChoices("suffix_invisible", "invisible_suffix"),
        description="The invisible part of the suffix that comes after suffix",
    )
    lang: ProgLang = "py3"
    execute_config: ExecuteConfig | None

    @computed_field(return_type=str)
    @property
    def solution_code(self):
        """The complete solution code with all prefix and suffix attached."""
        return "".join([self.prefix, self.solution, self.suffix, self.suffix_invisible])

    @computed_field(return_type=str)
    @property
    def template_code(self):
        """The complete template code with all prefix and suffix attached"""
        return "".join([self.prefix, self.template, self.suffix, self.suffix_invisible])


class ProQ(BaseModel):
    """Pydantic model for a Programming Question (ProQ)"""

    title: str | None = Field(validation_alias="Title", description="Title")
    statement: str = Field(
        validation_alias="Problem Statement", description="The problem statement"
    )
    public_testcases: list[TestCase] = Field(validation_alias="Public Test Cases")
    private_testcases: list[TestCase] = Field(validation_alias="Private Test Cases")
    solution: Solution = Field(validation_alias="Solution", description="The solution")

    class Config:
        validate_assignment = True
        populate_by_name = True

    @field_validator("title")
    @classmethod
    def remove_duplicates(cls, word):
        return re.sub(re.compile(r"\s+"), " ", word).strip()
