from pathlib import Path

import pytest

from proqtor.core_components import Solution
from proqtor.parse import extract_codeblock_content

fixtures = Path(__file__).parent / "solution_parse_fixtures.md"

with open(fixtures) as f:
    content = f.read().split("\n.\n")
    extraction_fixtures = []
    for i in range(0, len(content), 7):
        extraction_fixtures.append(
            {
                "title": content[i],
                "code": content[i + 1],
                "prefix": extract_codeblock_content(content[i + 2])["code"],
                "solution": extract_codeblock_content(content[i + 3])["code"],
                "template": extract_codeblock_content(content[i + 4])["code"],
                "suffix": extract_codeblock_content(content[i + 5])["code"],
                "solution_code": extract_codeblock_content(content[i + 6])["code"],
            }
        )


@pytest.mark.parametrize(
    "item",
    extraction_fixtures,
    ids=(item["title"] for item in extraction_fixtures),
)
def test_solution_extraction(item):
    block = Solution.from_code_block(item["code"])
    assert block.solution == item["solution"]


@pytest.mark.parametrize(
    "item",
    extraction_fixtures,
    ids=(item["title"] for item in extraction_fixtures),
)
def test_template_extraction(item):
    block = Solution.from_code_block(item["code"])
    assert block.template == item["template"]


@pytest.mark.parametrize(
    "item",
    extraction_fixtures,
    ids=(item["title"] for item in extraction_fixtures),
)
def test_prefix_extraction(item):
    block = Solution.from_code_block(item["code"])
    assert block.prefix == item["prefix"]


@pytest.mark.parametrize(
    "item",
    extraction_fixtures,
    ids=(item["title"] for item in extraction_fixtures),
)
def test_suffix_extraction(item):
    block = Solution.from_code_block(item["code"])
    assert block.suffix == item["suffix"]


@pytest.mark.parametrize(
    "item",
    extraction_fixtures,
    ids=(item["title"] for item in extraction_fixtures),
)
def test_solution_code_extraction(item):
    block = Solution.from_code_block(item["code"])
    assert block.solution_code == item["solution_code"]
