from md2json import dictify
from marko import Markdown
import yaml
import os
import re
from collections import namedtuple

ProqSet = namedtuple("ProqSet", ["unit_name", "proqs"])


def extract_codeblock_content(text):
    return (
        [
            block
            for block in Markdown().parse(text).children
            if (block.get_type() == "FencedCode" or block.get_type() == "CodeBlock")
        ][0]
        .children[0]
        .children
    )


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


def extract_solution(solution_template):
    code = {}
    solution_template = extract_codeblock_content(solution_template)
    for part in ["prefix", "suffix", "suffix_invisible", "template"]:
        code[part] = get_tag_content(part, solution_template)

    code["solution"] = code["template"]
    code["template"] = strip_tags(
        remove_tags(code["template"], ["solution", "sol"]), ["los"]
    )

    # opposite of sol will be in template but removed from solution
    code["solution"] = strip_tags(
        remove_tag(code["solution"], "los"), ["sol", "solution"]
    )
    return code


def extract_testcases(testcases_dict):
    testcases_list = list(testcases_dict.values())
    return [
        {
            "input": extract_codeblock_content(input),
            "output": extract_codeblock_content(output),
        }
        for input, output in zip(testcases_list[::2], testcases_list[1::2])
    ]


duplicate_whitespace_pattern = re.compile(r"\s+")


def remove_duplicate_whitespace(word):
    return re.sub(duplicate_whitespace_pattern, " ", word).strip()


from .template_utils import relative_env


def load_proq(proq_file):
    """Loads the proq file and returns a Proq"""
    md_file = relative_env.get_template(proq_file).render()
    _, yaml_header, md_string = md_file.split("---", 2)
    yaml_header = yaml.safe_load(yaml_header)

    all_proqs = []
    for unit_name, proqs in dictify(md_string).items():
        unit_name = remove_duplicate_whitespace(unit_name)
        for title, proq in proqs.items():
            proq["Unit Name"] = unit_name
            proq["Title"] = remove_duplicate_whitespace(title)
            proq["Solution"] = extract_solution(proq["Solution"])
            proq["Testcases"]["Public Testcases"] = extract_testcases(
                proq["Testcases"]["Public Testcases"]
            )
            proq["Testcases"]["Private Testcases"] = extract_testcases(
                proq["Testcases"]["Private Testcases"]
            )
            proq.update(yaml_header)
            all_proqs.append(proq)
    return all_proqs
