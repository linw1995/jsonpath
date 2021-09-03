# Standard Library
from typing import Any, Mapping, Optional


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

        func = getattr(pdm.pep517.api, name)

        if name == "build_wheel":

            def build_wheel(
                wheel_directory: str,
                config_settings: Optional[Mapping[str, Any]] = None,
                metadata_directory: Optional[str] = None,
            ) -> str:
                build_lark_parser()
                return func(wheel_directory, config_settings, metadata_directory)

            return build_wheel

        elif name == "build_sdist":

            def build_sdist(
                sdist_directory: str,
                config_settings: Optional[Mapping[str, Any]] = None,
            ) -> str:
                build_lark_parser()
                return func(sdist_directory, config_settings)

            return build_sdist

        else:
            return func

    except ImportError:
        return getattr(globals(), name)
