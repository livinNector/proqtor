import json
from importlib.resources import files
from typing import Annotated, Literal

from pydantic import BeforeValidator

# curl https://emkc.org/api/v2/piston/runtimes | \
#   jq "sort_by(.language)| map({language: .language, aliases: .aliases})" \
#   > runtimes.json

# langs and aliases taken from piston
runtimes = json.loads(files("proqtor.data").joinpath("runtimes.json").read_text())
alias_map = {runtime["language"]: runtime["language"] for runtime in runtimes} | {
    alias: runtime["language"] for runtime in runtimes for alias in runtime["aliases"]
}
alias_codes = sorted(list(alias_map.keys()))


class InvalidLangAliasError(ValueError):
    pass


def get_lang_code(alias):
    """Get the lang code from alias."""
    if alias not in alias_map:
        raise InvalidLangAliasError(
            f"Alias not recognized. Alias should be one of {alias_codes}"
        )
    return alias_map[alias]


ProgLang = Annotated[
    Literal[
        "awk",
        "bash",
        "basic",
        "basic.net",
        "befunge93",
        "bqn",
        "brachylog",
        "brainfuck",
        "c",
        "c++",
        "cjam",
        "clojure",
        "cobol",
        "coffeescript",
        "cow",
        "crystal",
        "csharp",
        "csharp.net",
        "d",
        "dart",
        "dash",
        "dragon",
        "elixir",
        "emacs",
        "emojicode",
        "erlang",
        "file",
        "forte",
        "forth",
        "fortran",
        "freebasic",
        "fsharp.net",
        "fsi",
        "go",
        "golfscript",
        "groovy",
        "haskell",
        "husk",
        "iverilog",
        "japt",
        "java",
        "javascript",
        "javascript",
        "jelly",
        "julia",
        "kotlin",
        "lisp",
        "llvm_ir",
        "lolcode",
        "lua",
        "matl",
        "matl",
        "nasm",
        "nasm64",
        "nim",
        "ocaml",
        "octave",
        "osabie",
        "paradoc",
        "pascal",
        "perl",
        "php",
        "ponylang",
        "powershell",
        "prolog",
        "pure",
        "pyth",
        "python",
        "python2",
        "racket",
        "raku",
        "retina",
        "rockstar",
        "rscript",
        "ruby",
        "rust",
        "samarium",
        "scala",
        "smalltalk",
        "sqlite3",
        "swift",
        "typescript",
        "typescript",
        "vlang",
        "vyxal",
        "yeethon",
        "zig",
    ],
    BeforeValidator(lambda x: alias_map[x]),
]
