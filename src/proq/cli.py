import fire

from . import create, evaluate, export


class ProqCli:
    """A Command-line suite for authoring Programming Questions.

    For help regarding individual commands use `proq [COMMAND] --help`.
    """

    def __init__(self) -> None:
        self.create = create.generate_template
        self.evaluate = evaluate.evaluate_proq_files
        self.export = export.proq_export


def main():
    fire.Fire(ProqCli(), name="proq")


if __name__ == "__main__":
    main()
