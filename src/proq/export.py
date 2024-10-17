import os
import argparse
import asyncio
from playwright.async_api import async_playwright

from .template_utils import package_env
from .parse import load_proq_from_file, load_nested_proq_from_file
from .models import NestedContent,ProQ

OUTPUT_FORMATS = ["json", "html", "pdf"]


async def print_html_to_pdf(html_content, output_pdf_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        await page.set_content(html_content)
        await page.pdf(path=output_pdf_path, print_background=True)
        await browser.close()

def get_rendered_html(nested_proq,show_hidden_suffix):
    return package_env.get_template(
        "proq_export_template.html.jinja"
    ).render(nested_proq=nested_proq, show_hidden_suffix=show_hidden_suffix)

def proq_export(proq_file, output_file=None, format="json", show_hidden_suffix=False):

    if not os.path.isfile(proq_file):
        raise FileNotFoundError(f"{proq_file} is not a valid file")

    if not output_file:
        assert (
            format in OUTPUT_FORMATS
        ), f"Export format not valid. Supported formats are {', '.join(OUTPUT_FORMATS[:-1])} and {OUTPUT_FORMATS[-1]}."
        output_file = ".".join(proq_file.split(".")[:-1]) + f".{format}"
    else:
        # infer format if output filename is given
        format = output_file.split('.')[-1]

    proq_file_format = proq_file.split(".")[-1]
    if proq_file_format == "yaml":
        nested_proq = load_nested_proq_from_file(proq_file)
    else:
        nested_proq = load_proq_from_file(proq_file)
        nested_proq = NestedContent[ProQ](title=nested_proq.title, content=nested_proq)


    with open(output_file, "w") as f:
        match format:
            case "json":
                f.write(nested_proq.model_dump_json(indent=2))
            case "html":
                f.write(get_rendered_html(nested_proq,show_hidden_suffix))
            case "pdf":
                asyncio.run(
                    print_html_to_pdf(
                        get_rendered_html(nested_proq, show_hidden_suffix), output_file
                    )
                )

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
