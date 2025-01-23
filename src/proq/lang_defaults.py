from importlib.resources import files

from .core_components import Solution
from .prog_langs import ProgLang

lang_default_files = files("proq.templates.lang_defaults")


def get_lang_block(lang):
    return lang_default_files.joinpath(f"{lang}.md").read_text("utf-8")


default_solution: dict[ProgLang, Solution] = {
    lang: Solution.from_code_block(get_lang_block(lang))
    for lang in ["python", "java", "c"]
}
