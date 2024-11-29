import asyncio
import os
import subprocess
import tempfile
from typing import Literal

from .core import NestedContent, ProQ, load_nested_proq_from_file
from .template_utils import package_env

OUTPUT_FORMATS = ["json", "html", "pdf"]


async def print_html_to_pdf(html_content, output_file, chrome_path=None):
    chrome_path = chrome_path or os.environ["CHROME"] or "chrome"
    with tempfile.NamedTemporaryFile(
        mode="w", delete_on_close=False, suffix=".html"
    ) as f:
        f.write(html_content)
        f.close()
        subprocess.run(
            [
                chrome_path,
                f"--print-to-pdf={output_file}",
                "--headless",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f.name,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )


def get_rendered_html(nested_proq, show_hidden_suffix, hide_private_testcases):
    return package_env.get_template("proq_export_template.html.jinja").render(
        nested_proq=nested_proq,
        show_hidden_suffix=show_hidden_suffix,
        hide_private_testcases=hide_private_testcases,
    )


def proq_export(
    proq_file: str | os.PathLike,
    output_file: str | os.PathLike = None,
    format: Literal["html", "json", "pdf"] = "html",
    show_hidden_suffix: bool = False,
    hide_private_testcases: bool = False,
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
        match format:
            case "json":
                if is_nested_proq:
                    f.write(nested_proq.model_dump_json(indent=2))
                else:
                    f.write(proq.model_dump_json(indent=2))
            case "html":
                f.write(
                    get_rendered_html(
                        nested_proq,
                        show_hidden_suffix=show_hidden_suffix,
                        hide_private_testcases=hide_private_testcases,
                    )
                )
            case "pdf":
                asyncio.run(
                    print_html_to_pdf(
                        get_rendered_html(
                            nested_proq,
                            show_hidden_suffix=show_hidden_suffix,
                            hide_private_testcases=hide_private_testcases,
                        ),
                        output_file,
                    )
                )

    print(f"Proqs dumped to {output_file}")
