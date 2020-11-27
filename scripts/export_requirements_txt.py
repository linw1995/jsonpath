"""
GitHub does not support poetry for creating dependency graph.
So use this script to export the requirements.txt file.
https://help.github.com/en/github/visualizing-repository-data-with-graphs/listing-the-packages-that-a-repository-depends-on#supported-package-ecosystems

Why not just use `poetry export -f requirements.txt` ?
Because it exports wrong dependencies, unlike the install process.
"""  # noqa: B950

# Standard Library
import os
import sys

from contextlib import redirect_stdout
from pathlib import Path


def export(
    path: Path,
    *extras,
    dev=False,
):
    # Standard Library
    from unittest import mock

    # Third Party Library
    from clikit.args import ArgvArgs
    from poetry.console.application import Application
    from poetry.puzzle.operations import Install, Update

    with mock.patch(
        "poetry.installation.installer.Installer._execute",
    ) as mocked_execute:
        app = Application()
        app.config.set_terminate_after_run(False)
        cmd = ["poetry", "install", "--dry-run"]
        if not dev:
            cmd.extend(["--no-dev"])

        for extra in extras:
            cmd.extend(["--extras", extra])

        with redirect_stdout(open(os.devnull, "w")):
            app.run(ArgvArgs(cmd))

        text = ""
        for call_args in mocked_execute.call_args_list:
            if sys.version_info[:2] > (3, 7):
                op = call_args.args[0]
            else:
                op = call_args[0][0]

            if not isinstance(op, (Install, Update)):
                continue

            if op.skip_reason in (
                "Not required",
                "Not needed for the current environment",
            ):
                continue

            package = op.package
            dependency = package.to_dependency()
            line = "{}=={}".format(package.name, package.version)
            requirement = dependency.to_pep_508()
            if ";" in requirement:
                line += "; {}".format(requirement.split(";")[1].strip())

            text += f"{line}\n"

        if path.exists() and path.read_text(encoding="utf-8") == text:
            return

        path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    export(Path("./requirements-mini.txt"), dev=False)
    export(Path("./requirements.txt"), "lark-parser", dev=False)
    export(
        Path("./requirements-dev.txt"),
        "lint",
        "test",
        "lark-parser",
        "docs",
        dev=True,
    )
