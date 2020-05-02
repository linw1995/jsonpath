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
    with open("jsonpath/lark_parser", "wb") as f:
        f.write(output)


def __getattr__(name):
    if name not in globals():
        import poetry.masonry.api

        if name in ("build_wheel", "build_sdist"):
            build_lark_parser()

        return getattr(poetry.masonry.api, name)

    return globals()[name]
