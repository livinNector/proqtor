#!/usr/bin/env python
import argparse
import os
from .template_utils import package_env
from .models import ExecuteConfig

default_lang_execute_config = {
    "python": ExecuteConfig(source_filename="test.py", run="python test.py"),
    "java": ExecuteConfig(
        source_filename="Test.java", build="javac Test.java", run="java Test.class"
    ),
    "c": ExecuteConfig(
        source_filename="test.c", build="gcc test.c -o test", run="./test"
    ),
}


def generate_template(output_file, lang, num_public, num_private):
    if os.path.isfile(output_file):
        raise FileExistsError(f"A file with the name '{output_file}' already exists.")

    template = package_env.get_template("proq_empty_template.md.jinja")
    content = template.render(
        lang=lang,
        num_public=num_public,
        num_private=num_private,
        **default_lang_execute_config.get(lang, ExecuteConfig()).model_dump(),
    )
    with open(output_file, "w") as f:
        f.write(content)


def configure_cli_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-o",
        "--output-file",
        type=str,
        help="Output file name",
        default="proq_template.md",
    )
    parser.add_argument(
        "-l", "--lang", type=str, help="Language of the proq", default="python"
    )
    parser.add_argument(
        "-npu", "--num-public", type=int, help="Number of public test cases", default=5
    )
    parser.add_argument(
        "-npr",
        "--num-private",
        type=int,
        help="Number of private test cases",
        default=5,
    )
    # TODO: implement multi file generation
    # parser.add_argument(
    #     "-np", "--num-problems", type=int, help="Number of problems", default=5
    # )
    # parser.add_argument(
    #     "--pattern", type=str, help="Problem numbering pattern", default="Problem {}"
    # )
    parser.set_defaults(
        func=lambda args: generate_template(
            args.output_file,
            args.lang,
            args.num_public,
            args.num_private,
        )
    )
