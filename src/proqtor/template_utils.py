from pathlib import Path

import yaml
from jinja2 import Environment, FunctionLoader, PackageLoader, select_autoescape
from marko.ext.gfm import gfm

package_env = Environment(
    loader=PackageLoader("proqtor", "templates"), autoescape=select_autoescape()
)
package_env.filters["gfm"] = gfm.convert


class YamlDumper(yaml.SafeDumper):
    pass


def flow_style_list(dumper, data):
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)


YamlDumper.add_representer(list, flow_style_list)

package_env.filters["yaml"] = lambda x: yaml.dump(x, Dumper=YamlDumper, sort_keys=False)


def load_relative_to(path):
    """Loads the files relative to the given file or directory."""

    def inner(template):
        nonlocal path
        path = Path(path)
        if not path.is_dir():
            path = path.parent
        return (path / template).read_text()

    return inner


def get_relative_env(filename):
    return Environment(
        loader=FunctionLoader(load_relative_to(filename)),
        autoescape=select_autoescape(),
        cache_size=0,
    )
