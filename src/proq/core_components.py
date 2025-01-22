import difflib

from pydantic import AliasChoices, BaseModel, Field

from .prog_langs import ProgLang


class TestCase(BaseModel):
    input: str
    output: str


class ExecuteConfig(BaseModel):
    source_filename: str | None = ""
    build: str | None = ""
    run: str | None = ""


SOL_OPEN = "<sol>"
SOL_CLOSE = "</sol>"
LOS_OPEN = "<los>"
LOS_CLOSE = "</los>"


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

    @property
    def template_solution_merge(self):
        differ = difflib.Differ()
        differences = differ.compare(self.template, self.solution)
        in_sol = False
        in_temp = False
        template = ""
        for diff in differences:
            if diff[0] == " ":
                if in_temp:
                    template += LOS_CLOSE
                    in_temp = False
                if in_sol:
                    template += SOL_CLOSE
                    in_sol = False
            elif diff[0] == "-" and not in_temp:
                template += LOS_OPEN
                in_temp = True
            elif diff[0] == "+" and not in_sol:
                template += SOL_OPEN
                in_sol = True
            template += diff[2]
        if in_temp:
            template += LOS_CLOSE
            in_temp = False
        if in_sol:
            template += SOL_CLOSE
            in_sol = False
        return template
