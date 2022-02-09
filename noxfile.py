# Standard Library
import os
import sys

from pathlib import Path

# Third Party Library
import nox

sys.path.insert(0, "")
# First Party Library
from jsonpath_build import build_lark_parser  # noqa: E402

nox.options.stop_on_first_error = True

pythons = ["3.7", "3.8", "3.9", "3.10"]

os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})
os.environ.pop("PYTHONPATH", None)

lark_parser_path = Path("jsonpath/lark_parser.py")


def get_nox_session_pybin(session):
    return session.bin + "/python"


@nox.session(python=pythons, reuse_venv=True)
@nox.parametrize(
    "parser_backend",
    [
        "standalone",
        "parser",
    ],
)
def coverage_test(session, parser_backend):
    session.run(
        "pdm",
        "sync",
        "--no-editable",
        "-v",
        "-G",
        "test",
        "-G",
        "parser",
        external=True,
    )
    if parser_backend == "standalone":
        if not lark_parser_path.exists():
            pybin_path = get_nox_session_pybin(session)
            build_lark_parser(pybin_path)

        session.run("pip", "uninstall", "lark", "-y")
    else:
        if lark_parser_path.exists():
            lark_parser_path.unlink()

    session.run("pytest", "-vv", "--cov=jsonpath", "--cov-append", *session.posargs)


@nox.session(python=pythons, reuse_venv=True)
def coverage_report(session):
    session.run("pdm", "sync", "--no-editable", "-v", "-G", "test", external=True)
    session.run("coverage", "report")
    session.run("coverage", "xml")
    session.run("coverage", "html")
    session.log(
        f">> open file:/{(Path() / 'htmlcov/index.html').absolute()} to see coverage"
    )


@nox.session(reuse_venv=True)
def build(session):
    if not lark_parser_path.exists():
        build_lark_parser()
    session.run("pdm", "build", external=True)


@nox.session(reuse_venv=True)
def build_readme(session):
    session.run(
        "pdm", "sync", "--no-editable", "-v", "-G", "build_readme", external=True
    )
    session.run(
        "python", "scripts/build_readme.py", "README.template.rst", "README.rst"
    )
