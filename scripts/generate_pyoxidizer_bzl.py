# Standard Library
import string
import sys

from pathlib import Path


def main():
    pyoxidizer_bzl_template_path = Path("./pyoxidizer.bzl.template")
    template = string.Template(pyoxidizer_bzl_template_path.read_text())
    try:
        text = template.substitute(
            wheel_path=next(Path("./dist").glob("*.whl"))
        )
    except StopIteration:
        sys.exit("no wheel release")

    Path("./pyoxidizer.bzl").write_text(text)


if __name__ == "__main__":
    main()
