import argparse
import re
import shlex

from marko import Markdown


def clip_extra_lines(text: str) -> str:
    """Reduces multiple consecutive line breaks to exactly two line breaks.

    Also strip blank lines in the beginning and end.
    """
    text = re.sub(r"\n\s*\n", "\n\n", text, flags=re.DOTALL).lstrip("\n")
    text = re.sub(r"\s*\n\s*$", "\n", text, flags=re.DOTALL)
    return text


def get_tag_content(tag: str, html: str) -> str:
    """Get the inner html of first match of a tag.

    Returns:
        Inner html if tag found else empty string
    """
    content = re.findall(f"<{re.escape(tag)}>(.*?)</{re.escape(tag)}>", html, re.DOTALL)
    content = content[0] if content and content[0].strip() else ""
    return content


def remove_tag(html, tag):
    return re.sub(
        f"<{re.escape(tag)}( .*?|)>(.*?)</{re.escape(tag)}>", "", html, flags=re.DOTALL
    )


def remove_tags(html, tags: list[str]):
    for tag in tags:
        html = remove_tag(html, tag)
    return html


def strip_tags(html: str, tags: list[str]) -> str:
    """Removes the given tags from an HTML text without removing the content."""
    return re.sub(
        r"<\/?({tags})( .*?|)>".format(tags="|".join(map(re.escape, tags))),
        "",
        html,
        flags=re.DOTALL,
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


def extract_code_parts(code):
    code_parts = re.match(
        r"(?P<prefix>.*)<template>(?P<tagged_template>.*)</template>(?P<suffix>.*)",
        code,
        re.DOTALL,
    )

    # Assume the whole code as solution if to tags are there
    if code_parts is None:
        return {
            "prefix": "",
            "suffix": "",
            "suffix_invisible": "",
            "tagged_template": "\n<sol>\n"
            f"{code}{"" if code[-1]=='\n' else '\n'}"
            "</sol>\n",
        }

    code_parts = code_parts.groupdict()

    # removing existing tags for backwards compatibility
    code_parts["prefix"] = strip_tags(code_parts["prefix"], ["prefix"]).lstrip()
    code_parts["suffix"] = strip_tags(code_parts["suffix"], ["suffix"])
    if "<suffix_invisible>" in code_parts["suffix"]:
        code_parts["suffix"], code_parts["suffix_invisible"] = code_parts[
            "suffix"
        ].split("<suffix_invisible>")
        code_parts["suffix_invisible"] = strip_tags(
            code_parts["suffix_invisible"], ["suffix_invisible"]
        ).rstrip()
    else:
        code_parts["suffix_invisible"] = ""

    if not code_parts["suffix"].strip():
        code_parts["suffix"] = ""
    elif not code_parts["suffix_invisible"]:
        code_parts["suffix"] = code_parts["suffix"].rstrip()

    return code_parts


def extract_solution(solution_codeblock):
    code_block_contents = extract_codeblock_content(solution_codeblock)
    code_parts = extract_code_parts(code_block_contents.pop("code"))
    return code_block_contents | code_parts


def extract_testcases(testcase_blocks: tuple):
    testcases_list = [x[1] for x in testcase_blocks]
    return [
        {
            "input": extract_codeblock_content(input)["code"],
            "output": extract_codeblock_content(output)["code"],
        }
        for input, output in zip(testcases_list[::2], testcases_list[1::2])
    ]
