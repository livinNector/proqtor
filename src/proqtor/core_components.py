import difflib
import warnings
from functools import cached_property
from importlib.resources import files

from pydantic import AliasChoices, BaseModel, Field, computed_field

from .parse import extract_solution, remove_tags, strip_tags
from .prog_langs import ProgLang
from .template_utils import package_env

lang_default_files = files("proqtor.templates.lang_defaults")
solution_template = package_env.get_template("solution.md.jinja")


def get_lang_default_code_block(lang):
    if lang not in ["python", "java", "c"]:
        lang = "python"
        warnings.warn(
            f"Default template for language {lang} not found. Defaulting to python."
        )
    return lang_default_files.joinpath(f"{lang}.md").read_text("utf-8")


class TestCase(BaseModel):
    input: str
    output: str


class ExecuteConfig(BaseModel):
    source_filename: str | None = ""
    build: str | None = ""
    run: str | None = ""


class Solution(BaseModel):
    prefix: str = Field(default="", description="The prefix of the solution")
    tagged_template: str = Field(
        default="",
        description="The part between prefix and suffix code where "
        "the parts only present in the solution is surrounded by <sol> tags "
        "and the parts only present in the template is surrounded by <los> tags.",
    )
    suffix: str = Field(default="", description="The suffix of the solution")
    suffix_invisible: str = Field(
        default="",
        validation_alias=AliasChoices("suffix_invisible", "invisible_suffix"),
        description="The invisible part of the suffix that comes after suffix",
    )
    lang: ProgLang = Field(default="python")
    execute_config: ExecuteConfig | None = Field(default_factory=ExecuteConfig)

    @classmethod
    def from_code_block(cls, code_block):
        """Creates the solution from template from markdown codeblock."""
        return cls(**extract_solution(code_block))

    @classmethod
    def from_default(cls, lang):
        """Creates a default solution from the default lang templates."""
        return cls.from_code_block(get_lang_default_code_block(lang=lang))

    @computed_field
    @cached_property
    def solution(self) -> str:
        """Template code between prefix and suffix extracted from tagged_template."""
        return strip_tags(
            remove_tags(self.tagged_template, ["los"]), ["sol", "solution"]
        )

    @computed_field
    @cached_property
    def template(self) -> str:
        """The solution code to replace template extracted from tagged_template."""
        return strip_tags(
            remove_tags(self.tagged_template, ["solution", "sol"]), ["los"]
        )

    def __setattr__(self, name, value):
        if name == "tagged_template":
            # Cache invalidation
            if hasattr(self, "solution"):
                del self.solution
            if hasattr(self, "template"):
                del self.template
        return super().__setattr__(name, value)

    def prefix_suffix_join(self, code):
        return "".join([self.prefix, code, self.suffix, self.suffix_invisible])

    @property
    def solution_code(self):
        """The complete solution code with all prefix and suffix attached."""
        return self.prefix_suffix_join(self.solution)

    @property
    def template_code(self):
        """The complete template code with all prefix and suffix attached."""
        return self.prefix_suffix_join(self.template)

    @property
    def template_solution_diff(self):
        differ = difflib.Differ()
        differences = differ.compare(
            self.template.splitlines(keepends=True),
            self.solution.splitlines(keepends=True),
        )
        return list(differences)

    @property
    def code_block(self):
        return solution_template.render(solution=self)
