from click import group
from importlib import import_module
from pkgutil import iter_modules

import plugins
from plugins.plugin_abstraction.command_line_register import RegisterFetchPlugin

@group(name="fetch")
def fetch_cli() -> None:
    """Use plugins to fetch card assets"""
    pass

def load_cli_fetch_plugins() -> None:
    for modinfo in iter_modules(plugins.__path__):
        module_name = f"{plugins.__name__}.{modinfo.name}.cli"
        try:
            module = import_module(module_name)
        except ModuleNotFoundError as e:
            continue

        register = getattr(module, "register_fetch", None)
        if callable(register):
            register_fetch: RegisterFetchPlugin = register
            register_fetch(fetch_cli)

load_cli_fetch_plugins()