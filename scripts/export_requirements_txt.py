# Standard Library
import enum
import shlex
import subprocess

from pathlib import Path

Format = enum.Enum("Format", "requirements setuppy")
BASE_DIR = Path(__file__).parent / "requirements"


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
    if not p.parent.exists():
        p.parent.mkdir(parents=True)
    is_new = not p.exists()
    if is_new or p.read_text() != output:
        p.write_text(output)
    if is_new:
        raise RuntimeError("Create a new file")


pdm_export(
    args=["--prod"],
    filename=BASE_DIR / "requirements-mini.txt",
    format=Format.requirements,
)
pdm_export(
    args=[
        "--prod",
        "-G:all",
    ],
    filename=BASE_DIR / "requirements.txt",
    format=Format.requirements,
)
pdm_export(
    args=["-G:all"],
    filename=BASE_DIR / "requirements-dev.txt",
    format=Format.requirements,
)
pdm_export(
    args=["-G", "docs"],
    filename=BASE_DIR / "requirements-docs.txt",
    format=Format.requirements,
)
# pdm_export(args=[], filename=BASE_DIR / "setup.py", format=Format.setuppy)
