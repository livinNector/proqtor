
import os 
import re
import yaml
import argparse
import shlex

from marko import Markdown
from md2json import dictify

from .template_utils import get_relative_env
from .models import ProQ


def clip_extra_lines(text: str) -> str:
    """
    Reduces sequences of more than two consecutive line breaks
    to exactly two line breaks.
    Also strip blank lines in the beginning and end.
    """

    text = re.sub(r"\n\s*\n", "\n\n", text, flags=re.DOTALL).lstrip("\n")
    text = re.sub(r"\s*\n\s*$", "\n", text, flags=re.DOTALL)
    return text


def get_tag_content(tag: str, html: str) -> str:
    """Get the inner html of first match of a tag.
    Returns empty string if tag not found
    """
    content = re.findall(f"<{re.escape(tag)}>(.*?)</{re.escape(tag)}>", html, re.DOTALL)
    content = clip_extra_lines(content[0]) if content else ""
    return content


def remove_tag(html, tag):
    return re.sub(
        f"<{re.escape(tag)}>(.*?)</{re.escape(tag)}>", "", html, flags=re.DOTALL
    )


def remove_tags(html, tags: list[str]):
    for tag in tags:
        html = remove_tag(html, tag)
    return html


def strip_tags(html: str, tags: list[str]) -> str:
    """Removes all tags from an HTML text."""
    return re.sub(
        r"<\/?({tags}).*?>".format(tags="|".join(tags)), "", html, flags=re.DOTALL
    )


execute_config_parser = argparse.ArgumentParser()
execute_config_parser.add_argument("source_filename", type=str, nargs="?")
execute_config_parser.add_argument("-b", "--build", type=str, required=False)
execute_config_parser.add_argument("-r", "--run", type=str, required=False)


def parse_execute_config(config_string):
    return dict(
        execute_config_parser.parse_args(shlex.split(config_string))._get_kwargs()
    )


def extract_codeblock_content(text):
    block = next(
        iter(
            block
            for block in Markdown().parse(text).children
            if (block.get_type() == "FencedCode" or block.get_type() == "CodeBlock")
        )
    )
    return {
        "lang": block.lang,
        "execute_config": parse_execute_config(block.extra),
        "code": block.children[0].children,
    }


def extract_solution(solution_codeblock):
    solution = extract_codeblock_content(solution_codeblock)
    solution_template = solution.pop('code')
    code = {}
    for part in ["prefix", "suffix", "suffix_invisible","invisible_suffix", "template"]:
        code[part] = get_tag_content(part, solution_template)

    code["solution"] = code["template"]
    code["template"] = strip_tags(
        remove_tags(code["template"], ["solution", "sol"]), ["los"]
    )

    # opposite of sol will be in template but removed from solution
    code["solution"] = strip_tags(
        remove_tag(code["solution"], "los"), ["sol", "solution"]
    )
    return solution|code


def extract_testcases(testcases_dict):
    testcases_list = list(testcases_dict.values())
    return [
        {
            "input": extract_codeblock_content(input)["code"],
            "output": extract_codeblock_content(output)["code"],
        }
        for input, output in zip(testcases_list[::2], testcases_list[1::2])
    ]


def load_proq_from_file(proq_file)->ProQ:
    """Loads the proq file and returns a Proq"""
    md_file = get_relative_env(proq_file).get_template(os.path.basename(proq_file)).render()
    yaml_header, md_string = md_file.split("---", 2)[1:]
    yaml_header = yaml.safe_load(yaml_header)
    proq = dictify(md_string)
    proq["Solution"] = extract_solution(proq["Solution"])
    proq["Public Test Cases"] = extract_testcases(proq["Public Test Cases"])
    proq["Private Test Cases"] = extract_testcases(proq["Private Test Cases"])
    proq.update(yaml_header)
    return ProQ.model_validate(proq)
