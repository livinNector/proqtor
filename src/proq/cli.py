import os
from typing import Literal

import fire

from . import evaluate, export
from .core import ProQ


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
    ):
        """Creates an empty proq file template with the given configuation.

        Args:
            output_file (str): Output file name
            lang (Literal["python","java","c"]) : Programming language used to
                create automatic execute configs.
                Possible values are python, java and c.
            n_public (int) : Number of public test cases
            n_private (int) : Number of private test cases
        """
        if os.path.isfile(output_file):
            raise FileExistsError(
                f"A file with the name '{output_file}' already exists."
            )

        ProQ.default_proq(
            lang=lang.lower().strip(), n_public=n_public, n_private=n_private
        ).to_file(output_file)


def main():
    fire.Fire(ProqCli(), name="proq")


if __name__ == "__main__":
    main()
