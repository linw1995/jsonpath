# Standard Library
import platform

from pathlib import Path

# Third Party Library
import nox
import nox.sessions

# First Party Library
from build import build_lark_parser


nox.options.stop_on_first_error = True

current_python_version = "%s.%s" % platform.python_version_tuple()[:2]


pythons = ["3.7", "3.8"]
assert current_python_version in pythons
pythons = [current_python_version]

lark_parser_path = Path("jsonpath/lark_parser.py")


@nox.session(python=pythons, reuse_venv=True)
@nox.parametrize(
    "parser_backend", ["standalone", "lark-parser"],
)
def test(session: nox.sessions.Session, parser_backend):
    session.run(
        "poetry",
        "install",
        "-v",
        "-E",
        "test",
        *(
            ("-E", parser_backend)
            if parser_backend == "lark-parser"
            else tuple()
        ),
        "--no-dev",
        external=True,
    )
    if "standalone":
        if not lark_parser_path.exists():
            build_lark_parser()
    else:
        if lark_parser_path.exists():
            lark_parser_path.unlink()

    session.run("pytest", "-vv", "--cov=jsonpath", "--cov-append")


@nox.session(reuse_venv=True)
def build(session):
    session.run("poetry", "install", "-v", "--no-dev", external=True)
    if not lark_parser_path.exists():
        build_lark_parser()
    session.run("poetry", "build", external=True)


@nox.session(python="3.7", reuse_venv=True)
def export_requirements_txt(session):
    session.install("poetry==1.0")
    session.run("python", "scripts/export_requirements_txt.py")
