# Standard Library
from typing import Any


def build_lark_parser(pybin_path=None) -> None:
    # Standard Library
    import subprocess
    import sys

    output = subprocess.check_output(
        args=[
            pybin_path or sys.executable,
            "-m",
            "lark.tools.standalone",
            "--maybe_placeholders",
            "jsonpath/grammar.lark",
        ]
    )
    with open("jsonpath/lark_parser.py", "wb") as f:
        f.write(output)


def __getattr__(name: str) -> Any:
    if name == "build_lark_parser":
        return build_lark_parser

    try:
        # Third Party Library
        import pdm.pep517.api

        if name in ("build_wheel", "build_sdist"):
            build_lark_parser()

        return getattr(pdm.pep517.api, name)
    except ImportError:
        return getattr(globals(), name)
