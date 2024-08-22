from pydantic import (
    BaseModel,
    Field,
    computed_field,
    TypeAdapter,
    AliasChoices,
    AliasPath,
)
from datetime import datetime
from typing import Literal, Optional


class SeekConfig(BaseModel):
    lang: str
    deadline: datetime
    evaluator: Literal["nsjail", "mooshak"] = "nsjail"
    evaluator_type: Literal["test_cases", "evaluation_script"] = "test_cases"
    ignore_presentation_error: bool = True
    allow_compile: bool = True
    show_sample_solution: bool = True
    is_public: bool = False


class LocalEvaluatorConfig(BaseModel):
    source_file: str
    build: Optional[str]
    run: str


class TestCase(BaseModel):
    input: str
    output: str


class TestCases(BaseModel):
    public_testcases: list[TestCase] = Field(
        validation_alias="Public Testcases", description="The public testcases"
    )
    private_testcases: list[TestCase] = Field(
        validation_alias="Private Testcases", description="The private testcases"
    )


from . import parse


class Solution(BaseModel):
    prefix: str = Field(description="The prefix of the solution")
    template: str = Field(description="Template code between prefix and suffix")
    solution: str = Field(description="The solution code to replace template")
    suffix: str = Field(description="The suffix of the solution")
    invisible_suffix: str = Field(
        validation_alias=AliasChoices("invisible_suffix", "suffix_invisible"),
        description="The invisible part of the suffix that comes after suffix",
    )

    @classmethod
    def from_solution_template(solution_template):
        """Extract the template from the solution template with tags for each sections"""
        return parse.extract_solution(solution_template=solution_template)

    @computed_field(return_type=str)
    @property
    def solution_code(self):
        """The complete solution code with all prefix and suffix attached."""
        return "".join([self.prefix, self.solution, self.suffix, self.invisible_suffix])

    @computed_field(return_type=str)
    @property
    def template_code(self):
        """The complete template code with all prefix and suffix attached"""
        return "".join([self.prefix, self.template, self.suffix, self.invisible_suffix])


class ProqV1(BaseModel):
    """Programming question version 1"""

    title: str = Field(validation_alias="Title", description="Title")
    lang: str = Field(
        description="Language code corresponding to the programming language."
    )
    statement: str = Field(
        validation_alias="Problem Statement", description="The problem statement"
    )
    public_testcases: list[TestCase] = Field(
        validation_alias=AliasPath("Testcases", "Public Testcases"),
        description="The Public and Private Testcases",
    )
    private_testcases: list[TestCase] = Field(
        validation_alias=AliasPath("Testcases", "Private Testcases"),
        description="The Public and Private Testcases",
    )
    solution: Solution = Field(validation_alias="Solution", description="The solution")
    seek_config: Optional[SeekConfig]
    local_evaluator_config: Optional[LocalEvaluatorConfig] = Field(
        validation_alias="local_evaluate"
    )


ProqsV1 = TypeAdapter(list[ProqV1])


class ProqV2(BaseModel):
    title: str = Field(description="The unique slug describing the question")
    is_lang_specific: str = Field(
        description="Whether the question is language specific"
    )
    statement: str = Field(description="The problem statement")
    examples: Optional[str] = Field(
        description="Examples with sample input and output with explanation"
    )
    assumptions: Optional[str] = Field(
        description="Assumptions/constraints about the problem"
    )
    public_testcases: list[TestCases] = Field(description="The public testcases")
    private_testcases: list[TestCases] = Field(description="The private testcases")
    solution: Solution = Field(description="The solution")
    solution_template: str = Field(description="")

    # @computed_field
    # @cached_property
