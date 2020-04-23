try:
    from lark import *
    from lark.exceptions import *
except ImportError:
    import importlib.resources

    exec(importlib.resources.read_text(__name__.split(".")[0], "lark"))
