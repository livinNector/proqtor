import asyncio
import os
import subprocess
import tempfile
from typing import Literal

from proqtor.core import NestedContent, ProQ, load_nested_proq_from_file
from proqtor.template_utils import package_env

OUTPUT_FORMATS = ["json", "html", "pdf"]


async def print_html_to_pdf(html_content, output_file, chrome_path=None):
    chrome_path = chrome_path or os.environ["CHROME"] or "chrome"
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "output.html")
        with open(file_path, "w") as f:
            f.write(html_content)
        subprocess.run(
            [
                chrome_path,
                f"--print-to-pdf={output_file}",
                "--headless",
                "--disable-gpu",
                "--no-pdf-header-footer",
                os.path.abspath(file_path),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


get_rendered_html = package_env.get_template("proq_export_template.html.jinja").render


def proq_export(
    proq_file: str | os.PathLike,
    output_file: str | os.PathLike = None,
    format: Literal["html", "json", "pdf"] = "html",
    show_hidden_suffix: bool = False,
    hide_private_testcases: bool = False,
    hide_template_diff: bool = False,
):
    """Export the proq_file or a nested proq config file to the given format.

    If the output file name is not given the output file will have
    same name as proq file but with the exported extension.

    Supports json, html and pdf formats.

    PDF export uses default chrome installation.
    It uses "chrome" as the default executable name.
    Different executable can be configured using CHROME environment variable.


    Args:
        proq_file (str|PathLike) : Name of the proq file.
        output_file (str) : Name of the output file.
        format (Literal["html", "json", "pdf"]) : Format to export.
        show_hidden_suffix (bool) :
            Whether to expand hidden suffix in HTML or PDF exports.
        hide_private_testcases (bool):
            Whether to hide private testcases in HTML or PDF exports.
        hide_template_diff (bool):
            Whether to hide the template - solution diff.

    """
    if not os.path.isfile(proq_file):
        raise FileNotFoundError(f"File {proq_file} does not exists.")
    if not output_file:
        assert format in OUTPUT_FORMATS, (
            "Export format not valid. Supported formats are "
            f"{', '.join(OUTPUT_FORMATS[:-1])} and {OUTPUT_FORMATS[-1]}."
        )
        output_file = ".".join(proq_file.split(".")[:-1]) + f".{format}"
    else:
        # infer format if output filename is given
        format = output_file.split(".")[-1]

    is_nested_proq = proq_file.split(".")[-1] == "yaml"
    if is_nested_proq:
        nested_proq = load_nested_proq_from_file(proq_file)
    else:
        proq = ProQ.from_file(proq_file)
        nested_proq = NestedContent[ProQ](title=proq.title, content=proq)

    with open(output_file, "w") as f:
        if format == "json":
            if is_nested_proq:
                f.write(nested_proq.model_dump_json(indent=2))
            else:
                f.write(proq.model_dump_json(indent=2))
        elif format in ["html", "pdf"]:
            rendered_html = get_rendered_html(
                nested_proq=nested_proq,
                show_hidden_suffix=show_hidden_suffix,
                hide_private_testcases=hide_private_testcases,
                hide_template_diff=hide_template_diff,
            )
            if format == "html":
                f.write(rendered_html)
            if format == "pdf":
                asyncio.run(
                    print_html_to_pdf(
                        rendered_html,
                        output_file,
                    )
                )

    print(f"Proqs dumped to {output_file}")
