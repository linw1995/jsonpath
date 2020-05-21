def build_lark_parser():
    import sys
    import subprocess

    output = subprocess.check_output(
        args=[
            sys.executable,
            "-m",
            "lark.tools.standalone",
            "jsonpath/grammar.lark",
        ]
    )
    with open("jsonpath/lark_parser.py", "wb") as f:
        f.write(output)


def __getattr__(name):
    if name == "build_lark_parser":
        return build_lark_parser

    try:
        import poetry.masonry.api

        if name in ("build_wheel", "build_sdist"):
            build_lark_parser()

        return getattr(poetry.masonry.api, name)
    except ImportError:
        return getattr(globals(), name)
