import os
from marko.ext.gfm import gfm
from jinja2 import Environment, PackageLoader, FunctionLoader, select_autoescape

package_env = Environment(
    loader=PackageLoader("proq", "templates"), autoescape=select_autoescape()
)
package_env.filters["gfm"] = gfm.convert


def load_relative_to(template):
    dir = os.path.dirname(template)
    path = os.path.abspath(os.path.join(dir, template))
    with open(path) as f:
        return f.read()


relative_env = Environment(
    loader=FunctionLoader(load_relative_to),
    autoescape=select_autoescape(),
    cache_size=0,
)
