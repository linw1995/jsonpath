# Standard Library
from pathlib import Path

# Third Party Library
import sybil

from sybil.parsers.rest import DocTestParser, PythonCodeBlockParser

ignore_collect = {
    p.absolute()
    for pattern in ["jsonpath/lark_parser.py"]
    for p in Path().glob(pattern)
}


def pytest_ignore_collect(collection_path, config):
    """return True to prevent considering this path for collection.
    This hook is consulted for all files and directories prior to calling
    more specific hooks.
    """
    if collection_path.absolute() in ignore_collect:
        return True

    return False


pytest_collect_file = sybil.Sybil(
    parsers=[
        DocTestParser(),
        PythonCodeBlockParser(),
    ],
    pattern="*.rst",
    fixtures=[],
).pytest()
