"""
Watch related files, build and serve Sphinx documentation automatically.
"""
# Standard Library
import os
import shlex
import subprocess
import sys

# Third Party Library
from livereload import Server


def shell(cmd, output=None, cwd=None, env=None, shell=False):
    if output is None:
        output = subprocess.DEVNULL

    if not isinstance(cmd, (list, tuple)) and not shell:
        cmd = shlex.split(cmd)

    def run():
        p = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=output,
            stderr=output,
            cwd=cwd,
            shell=shell,
            env=env or os.environ.copy(),
        )
        p.wait()

    return run


def main():
    server = Server()

    # https://github.com/pypa/virtualenv/issues/906#issuecomment-244394963
    # the Python executable from virtualenv
    # doesn't set the PATH or VIRTUAL_ENV environment variables.
    # That's by design, and is not a bug.
    env = os.environ.copy()
    env["PATH"] = (
        os.path.dirname(os.path.abspath(sys.executable))
        + os.pathsep
        + os.environ.get("PATH", "")
    )
    build_docs = shell("make html", cwd="docs", output=sys.stderr, env=env)
    # watcher use glob.glob without setting recursive=True
    # ref:
    # https://github.com/lepture/python-livereload/pull/203
    # https://docs.python.org/3/library/glob.html#glob.glob
    server.watch("docs/source/*.rst", build_docs)
    server.watch("docs/source/**/*.rst", build_docs)
    server.watch("jsonpath/*.py", build_docs)
    server.watch("jsonpath/**/*.py", build_docs)
    server.serve(root="docs/build/html")


if __name__ == "__main__":
    main()
