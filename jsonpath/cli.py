# Standard Library
import argparse
import json
import sys

from pathlib import Path

# Local Folder
from .core import JSONPathError
from .parser import parse


def cli(args: argparse.Namespace) -> None:
    try:
        jp = parse(args.expression)
    except JSONPathError as exc:
        raise SystemExit(str(exc)) from exc

    if args.file:
        file_path = Path(args.file)
        try:
            with file_path.open() as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"Error reading {file_path}: {exc}") from exc
    elif not sys.stdin.isatty():
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON from stdin: {exc}") from exc
    else:
        raise SystemExit("JSON file is needed.")

    json.dump(jp.find(data), sys.stdout, indent=2, ensure_ascii=args.ensure_ascii)
    sys.stdout.write("\n")


def create_args_parser() -> argparse.ArgumentParser:
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("expression", help="JSONPath expression")
    args_parser.add_argument(
        "-f",
        "--file",
        help="JSON file need to be parsed and extracted by JSONPath expression",
    )
    args_parser.add_argument(
        "--ensure-ascii",
        help="Escape all non-ASCII characters from extracting results",
        action="store_true",
    )
    return args_parser


def main() -> None:
    args_parser = create_args_parser()
    args = args_parser.parse_args()
    cli(args)


if __name__ == "__main__":
    main()
