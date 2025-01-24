import os
from typing import Literal

import fire
from termcolor import cprint

from proq.core import ProQ

from . import evaluate, export
from .utils import color_diff


class ProqCli:
    """A Command-line suite for authoring Programming Questions.

    For help regarding individual commands use `proq [COMMAND] --help`.
    """

    def __init__(self) -> None:
        self.evaluate = evaluate.evaluate_proq_files
        self.export = export.proq_export

    def create(
        self,
        output_file: str,
        lang: Literal["python", "java", "c"] = "python",
        n_public: int = 5,
        n_private: int = 5,
        force: bool = False,
    ):
        """Creates an empty proq file template with the given configuation.

        Args:
            output_file (str): Output file name
            lang (Literal["python","java","c"]) : Programming language used to
                create automatic execute configs.
                Possible values are python, java and c.
            n_public (int) : Number of public test cases
            n_private (int) : Number of private test cases
            force (bool) : Overwrite file if exists
        """
        if not force and os.path.isfile(output_file):
            raise FileExistsError(
                f"A file with the name '{output_file}' already exists."
            )

        ProQ.default_proq(
            lang=lang.lower().strip(), n_public=n_public, n_private=n_private
        ).to_file(output_file)

    def format(self, *proq_files: list[str]):
        """Formats the given files according to the proq template."""
        for proq_file in proq_files:
            ProQ.from_file(proq_file, render_template=False).to_file(proq_file)

    def correct(self, *proq_files: list[str]):
        """Corrects the test case outputs according to the solution."""
        for proq_file in proq_files:
            try:
                proq = ProQ.from_file(proq_file).correct_outputs(inplace=True)
                unrendered_proq = ProQ.from_file(proq_file, render_template=False)
                unrendered_proq.public_test_cases = proq.public_test_cases
                unrendered_proq.private_test_cases = proq.private_test_cases
                unrendered_proq.to_file(proq_file)

            except FileNotFoundError:
                print(f"{proq_file} is not a valid file.")

    def show_code(self, proq_file: str, render: bool = False):
        """Prints the whole solution where each part are highlighted.

        Args:
            proq_file (str): The proq file.
            render (bool): Whether to render the jinja template
        """
        proq = ProQ.from_file(proq_file, render_template=render)
        cprint(proq.solution.prefix, color="grey", end="")
        color_diff(proq.solution.template, proq.solution.solution)
        if proq.solution.suffix:
            cprint(proq.solution.suffix, color="grey", end="")
        if proq.solution.suffix_invisible:
            cprint(proq.solution.suffix_invisible, on_color="on_light_grey")


def main():
    fire.Fire(ProqCli(), name="proq")


if __name__ == "__main__":
    main()
