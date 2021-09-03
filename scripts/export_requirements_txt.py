# Standard Library
import enum
import shlex
import subprocess

from pathlib import Path

Format = enum.Enum("Format", "requirements setuppy")


def fix_end_of_file(text):
    return text.rstrip() + "\n"


def pdm_export(args, filename, format: Format):

    output = subprocess.check_output(
        shlex.split(f"pdm export -f {format.name} {' '.join(args)}"), encoding="utf-8"
    )
    output = fix_end_of_file(output)
    if format is Format.setuppy:
        output = "\n".join(
            ['# This a dummy setup.py to enable GitHub "Used By" stats', output]
        )

    p = Path(filename)
    is_new = not p.exists()
    if is_new or p.read_text() != output:
        p.write_text(output)

    if is_new:
        raise RuntimeError("Create a new file")


pdm_export(
    args=["--prod"], filename="requirements-mini.txt", format=Format.requirements
)
pdm_export(
    args=[
        "--prod",
        "-G:all",
    ],
    filename="requirements.txt",
    format=Format.requirements,
)
pdm_export(args=["-G:all"], filename="requirements-dev.txt", format=Format.requirements)
pdm_export(
    args=["-G", "docs"], filename="requirements-docs.txt", format=Format.requirements
)
# pdm_export(args=[], filename="setup.py", format=Format.setuppy)
