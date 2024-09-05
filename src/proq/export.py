import os
import argparse
import asyncio
from playwright.async_api import async_playwright

from .template_utils import package_env
from .parse import load_proqsets_from_yaml
from .models import ProqSets

OUTPUT_FORMATS = ["json",  "html", "pdf"]


async def print_html_to_pdf(html_content, output_pdf_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        await page.set_content(html_content)
        await page.pdf(path=output_pdf_path, print_background=True)
        await browser.close()


def proq_export(yaml_file, output_file=None, format="json", show_hidden_suffix=False):
    # TODO: support different nested levels of yaml
    if not os.path.isfile(yaml_file):
        raise FileNotFoundError(f"{yaml_file} is not a valid file")

    if not output_file:
        assert (
            format in OUTPUT_FORMATS
        ), f"Export format not valid. Supported formats are {', '.join(OUTPUT_FORMATS[:-1])} and {OUTPUT_FORMATS[-1]}."
        output_file = ".".join(yaml_file.split(".")[:-1]) + f".{format}"

    proq_sets = load_proqsets_from_yaml(yaml_file)
    with open(output_file, "w") as f:
        if format == "json":
            f.write(ProqSets.dump_json(proq_sets, indent=2).decode("utf-8"))
        rendered_html = package_env.get_template(
            "proq_export_template.html.jinja"
        ).render(proq_sets=proq_sets, show_hidden_suffix=show_hidden_suffix)

        if format == "html":
            with open(output_file, "w") as f:
                f.write(rendered_html)
        elif format == "pdf":
            asyncio.run(print_html_to_pdf(rendered_html, output_file))

    print(f"Proqs dumped to {output_file}")


def conifgure_cli_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "proq_file", metavar="F", type=str, help="proq file to be exported"
    )
    parser.add_argument(
        "-o",
        "--output-file",
        metavar="OUTPUT_FILE",
        required=False,
        type=str,
        help="name of the output file.",
    )
    parser.add_argument(
        "-f",
        "--format",
        metavar="OUTPUT_FORMAT",
        choices=OUTPUT_FORMATS,
        default="json",
        help="format of the output file export",
    )
    parser.add_argument(
        "--show-hidden-suffix",
        action="store_true",
        help="Show hidden suffix in the render for HTML and PDF",
        required=False,
    )
    parser.set_defaults(
        func=lambda args: proq_export(
            args.proq_file, args.output_file, args.format, args.show_hidden_suffix
        )
    )
