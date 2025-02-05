import pathlib

import pytest

from proqtor.core_components import Solution

template_dir = pathlib.Path(__file__).parent / "solution_templates"


def get_solution_template(name):
    return (template_dir / f"{name}.md").read_text()


@pytest.mark.parametrize(
    "file_name",
    (
        "only_template",
        "no_execute_config",
        "with_prefix_and_suffix",
        "with_invisible_suffix",
        "with_suffix_and_invisible_suffix",
    ),
)
def test_parse_render(file_name):
    code_block = get_solution_template(file_name)
    parsed = Solution.from_code_block(code_block)
    rendered = Solution.from_code_block(parsed.code_block)
    assert parsed.code_block == rendered.code_block == code_block


@pytest.mark.parametrize(
    "unformatted,formatted",
    (
        ("no_template", "only_solution"),
        ("blank_prefix", "only_template"),
        ("blank_suffix_and_invisible_suffix", "only_template"),
        ("blank_suffix", "only_template"),
        ("blank_suffix_and_unstripped_invisible_suffix", "with_invisible_suffix"),
        ("unstripped_invisible_suffix", "with_suffix_and_invisible_suffix"),
        ("unstripped_prefix_and_suffix", "with_prefix_and_suffix"),
    ),
)
def test_formatting(unformatted, formatted):
    code_block = get_solution_template(unformatted)
    formatted = get_solution_template(formatted)
    parsed = Solution.from_code_block(code_block)
    rendered = Solution.from_code_block(parsed.code_block)
    assert parsed.code_block == rendered.code_block == formatted
