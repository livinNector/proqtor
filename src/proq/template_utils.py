import os
from marko.ext.gfm import gfm
from jinja2 import Environment, PackageLoader, FunctionLoader, select_autoescape

package_env = Environment(
    loader=PackageLoader("proq", "templates"), autoescape=select_autoescape()
)
package_env.filters["gfm"] = gfm.convert

def load_relative_to(filename):
    def inner(template):
        dir = os.path.dirname(filename)
        path = os.path.abspath(os.path.join(dir,template))
        with open(path) as f:
            return f.read()
    return inner

def get_relative_env(filename):
    return Environment(
        loader=FunctionLoader(load_relative_to(filename)),
        autoescape=select_autoescape(),
        cache_size=0,
    )
