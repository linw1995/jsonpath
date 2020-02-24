"""
Watch related files, build and serve Sphinx documentation automatically.
"""
# Standard Library
import os
import shlex
import subprocess

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
    build_docs = shell("make html", cwd="docs")
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
