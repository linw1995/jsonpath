"""

.. _issues-172: https://github.com/github/markup/issues/172

Because Github markup do not render :include: directive. (issues-172_)
"""
# Standard Library
from pathlib import Path
from unittest import mock

# Third Party Library
import click
import docutils.nodes
import docutils.parsers.rst
import docutils.parsers.rst.directives.misc
import docutils.statemachine
import docutils.utils


@click.command()
@click.argument("source_file")
@click.argument("target_file")
def build_readme(source_file, target_file):
    old_string2lines = docutils.statemachine.string2lines
    old_run = docutils.parsers.rst.directives.misc.Include.run
    text = ""
    target_text = None

    def string2lines(*args, **kwargs):
        nonlocal text, target_text
        if target_text is not None:
            text = text.replace(target_text, args[0])
            target_text = None
        else:
            text += args[0]

        rv = old_string2lines(*args, **kwargs)
        return rv

    def run(self):
        nonlocal target_text
        target_text = self.block_text
        rv = old_run(self)
        return rv

    with mock.patch.object(
        docutils.statemachine, "string2lines", string2lines
    ), mock.patch.object(
        docutils.parsers.rst.directives.misc.Include, "run", run
    ):
        source_file_path: Path = Path.cwd() / source_file
        target_file_path: Path = Path.cwd() / target_file
        parser = docutils.parsers.rst.Parser()
        default_settings = docutils.frontend.OptionParser(
            components=(docutils.parsers.rst.Parser,)
        ).get_default_values()
        document = docutils.utils.new_document(
            source_file_path.name, default_settings
        )
        parser.parse(source_file_path.read_text(encoding="utf-8"), document)
        text = text.rstrip() + "\n"
        if (
            target_file_path.exists()
            and target_file_path.read_text(encoding="utf-8") == text
        ):
            return

        target_file_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    build_readme()
