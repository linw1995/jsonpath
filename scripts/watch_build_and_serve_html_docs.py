"""
Watch related files, build and serve Sphinx documentation automatically.
"""
# Third Party Library
from livereload import Server, shell


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
