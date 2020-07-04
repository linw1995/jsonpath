# Standard Library
from pathlib import Path


ignore_collect = sum(
    (
        [str(p.absolute()) for p in Path().glob(pattern)]
        for pattern in ["jsonpath/lark_parser.py"]
    ),
    start=[],
)


def pytest_ignore_collect(path, config):
    """ return True to prevent considering this path for collection.
    This hook is consulted for all files and directories prior to calling
    more specific hooks.
    """
    # https://docs.pytest.org/en/5.4.3/reference.html?highlight=pytest_ignore_collect#_pytest.hookspec.pytest_ignore_collect # noqa: B950
    if str(path) in ignore_collect:
        return True

    return False
