import pathlib

import pytest

from proq.core_components import Solution


def get_solution_templates():
    template_dir = pathlib.Path(__file__).parent / "solution_templates"
    return [file.read_text() for file in template_dir.glob("*")]


@pytest.mark.parametrize("code_block", get_solution_templates())
def test_solution(code_block):
    parsed = Solution.from_code_block(code_block)
    rendered = Solution.from_code_block(parsed.code_block)
    assert parsed.code_block == rendered.code_block
