#!/usr/bin/env python
import os
from typing import Literal

from .core import ExecuteConfig
from .template_utils import package_env

default_lang_execute_config = {
    "python": ExecuteConfig(source_filename="test.py", run="python test.py"),
    "java": ExecuteConfig(
        source_filename="Test.java", build="javac Test.java", run="java Test.class"
    ),
    "c": ExecuteConfig(
        source_filename="test.c", build="gcc test.c -o test", run="./test"
    ),
}


def generate_template(
    output_file: str,
    lang: Literal["python", "java", "c"] = "python",
    num_public: int = 5,
    num_private: int = 5,
):
    """Creates an empty proq file template with the given configuation.

    Args:
        output_file (str): Output file name
        lang (Literal["python","java","c"]) : Programming language used to
            create automatic execute configs.
            Possible values are python, java and c.
        num_public (int) : Number of public test cases
        num_private (int) : Number of private test cases
    """
    lang = lang.lower().strip()
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
