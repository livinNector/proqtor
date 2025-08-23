import os
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Literal

import fire
from termcolor import cprint

from proqtor.core import ProQ, ProqParseError
from proqtor.evaluate_utils import ProqCheck
from proqtor.utils import color_diff

from . import export

try:
    from proqtor.gen_ai_utils import generate_proq

    gen_ai_features = True
except ImportError:
    gen_ai_features = False


@contextmanager
def ignore_parse_errors():
    try:
        yield
    except FileNotFoundError as e:
        print(f"{e.filename} is not a valid file.")
    except ProqParseError as e:
        print("ProqParseError:", e.message)
    except Exception as e:
        print(e)


def ignore_parse_error_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with ignore_parse_errors():
            func(*args, **kwargs)

    return wrapper


class ProqCli:
    """A Command-line suite for authoring Programming Questions.

    For help regarding individual commands use `proq [COMMAND] --help`.
    """

    def __init__(self) -> None:
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

    def format(self, *proq_files: list[str], asciify=False):
        """Formats the given files according to the proq template.

        Args:
            proq_files (list[str]): List of proq files to format.
            asciify (bool):
                Whether to convert non ascii chars to ascii.
        """
        for proq_file in proq_files:
            with ignore_parse_errors():
                ProQ.from_file(proq_file, render_template=False).to_file(
                    proq_file, asciify=asciify
                )

    def correct(self, *proq_files: list[str]):
        """Corrects the test case outputs according to the solution.

        Args:
            proq_files (list[str]): List of proq files to correct.
        """
        for proq_file in proq_files:
            with ignore_parse_errors():
                proq = ProQ.from_file(proq_file).correct_outputs(inplace=True)
                unrendered_proq = ProQ.from_file(proq_file, render_template=False)
                unrendered_proq.public_test_cases = proq.public_test_cases
                unrendered_proq.private_test_cases = proq.private_test_cases
                unrendered_proq.to_file(proq_file)

    def run(self, proq_file: str):
        """Runs the solution as it is run from the terminal."""
        proq = ProQ.from_file(proq_file=proq_file, render_template=True)
        proq.run()

    @ignore_parse_error_wrapper
    def show_code(
        self,
        proq_file: str,
        render: bool = False,
        mode: Literal["solution", "template", "diff"] = "diff",
    ):
        """Prints the whole solution where each part are highlighted.

        Args:
            proq_file (str): The proq file.
            render (bool): Whether to render the jinja template
            mode (Literal["solution", "template", "diff"]): Display mode
        """
        proq = ProQ.from_file(proq_file, render_template=render)
        cprint(proq.solution.prefix, color="grey", end="")
        if mode == "diff":
            color_diff(proq.solution.template, proq.solution.solution)
        elif mode == "solution":
            print(proq.solution.solution)
        elif mode == "template":
            print(proq.solution.template)
        if proq.solution.suffix:
            cprint(proq.solution.suffix, color="grey", end="")
        if proq.solution.suffix_invisible:
            cprint(proq.solution.suffix_invisible, on_color="on_light_grey")

    @ignore_parse_error_wrapper
    def export_test_cases(self, proq_file, zip: bool = False):
        """Exports the test cases into a folder.

        Args:
            proq_file (str): The proq file
            zip (bool): Whether to zip archive instead of a folder.
        """
        proq = ProQ.from_file(proq_file)
        folder = Path(os.path.splitext(proq_file)[0])
        proq.export_test_cases(folder, zip)

    def evaluate(self, *files: str | os.PathLike, verbose=False, diff_mode=False):
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
            with ignore_parse_errors():
                proq = ProQ.from_file(file_path)

                result = proq.evaluate(verbose=verbose, diff_mode=diff_mode)
                if verbose:
                    print()
                proq_checks.append((file_path, result))

        n_proqs = len(proq_checks)
        cprint(
            f"Total of {n_proqs} proq{'s' if n_proqs > 1 else ''} evaluated.",
            attrs=["bold"],
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

    if gen_ai_features:

        def generate(
            self,
            prompt: str,
            *examples: list[str],
            output_file: str = None,
            model: str = "groq:gemma2-9b-it",
        ):
            """Generates a new proq file based on the given prompt and examples.

            Args:
                prompt (str): The prompt describing the new proq
                examples (str): The file paths to the example proqs
                output_file (str): The file name to store the output.
                    If not provided, the snake cased version of the title
                    generated will be used as the file name.
                model (str):
                    The LLM model to be used in the format of "provider:model_id".
                    The currently supported providers are groq and open-ai.
            """
            try:
                proq = generate_proq(prompt, example_files=examples, model=model)
            except ProqParseError as e:
                print("Genrated Proq is not in the required format:", e.message)
                with open(output_file, "w") as f:
                    f.write(e.content)
            else:
                if output_file is None:
                    output_file = proq.title.lower().replace(" ", "_") + ".md"
                proq.to_file(output_file)
            print(f"Output is saved to {output_file}")
    else:

        def generate(self):
            print(
                "Gen AI features are not installed. To use Gen AI features install the "
                "optional dependencies proqtor[genai]"
            )


def main():
    fire.Fire(ProqCli(), name="proq")


if __name__ == "__main__":
    main()
