from typing import Literal

from marko import Markdown
from marko.md_renderer import MarkdownRenderer


def fold_level(content, level, return_type: Literal["list", "dict"] = "dict"):
    """Takes a markdown content and returns a folded dict with one heading level."""
    document = Markdown().parse(content)
    heading = None
    if return_type == "dict":
        folded_blocks = {}
    elif return_type == "list":
        folded_blocks = []

    for block in document.children:
        if block.get_type() == "Heading" and block.level == level:
            heading = block.children[0].children
            if return_type == "dict":
                folded_blocks[heading] = []
                current_blocks = folded_blocks[heading]
            elif return_type == "list":
                folded_blocks.append([heading, []])
                current_blocks = folded_blocks[-1][-1]
        elif heading:
            current_blocks.append(block)
    renderer = MarkdownRenderer()
    folded_blocks = [
        (level_heading, "".join(renderer.render(block) for block in blocks))
        for level_heading, blocks in (
            folded_blocks.items() if return_type == "dict" else folded_blocks
        )
    ]
    if return_type == "dict":
        folded_blocks = dict(folded_blocks)
    return folded_blocks


def dictify(content):
    """Converts the markdown text to dictionaries based on heading outline."""

    def nest_blocks(blocks, level):
        current_block = None
        inner_blocks = {}
        for block in blocks:
            if block.get_type() == "Heading" and block.level == level:
                current_block = block.children[0].children
                inner_blocks[current_block] = []
            elif current_block:
                inner_blocks[current_block].append(block)
        if not current_block:
            renderer = MarkdownRenderer()
            return "".join(renderer.render(block) for block in blocks)
        return {
            block_name: nest_blocks(children, level + 1)
            for block_name, children in inner_blocks.items()
        }

    document = Markdown().parse(content)
    return nest_blocks(document.children, 1)


def undictify(nested_dict, level=1):
    """Converts the nested dictionary back into markdown text."""
    markdown_text = ""
    for heading, content in nested_dict.items():
        markdown_text += f"{'#' * level} {heading}\n\n"
        if isinstance(content, dict):
            markdown_text += undictify(content, level + 1)
        else:
            markdown_text += f"{content}\n\n"
    return markdown_text
