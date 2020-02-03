# Standard Library
import json
import os
import sys

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

# Third Party Library
import pytest

# First Party Library
from jsonpath.cli import cli, create_args_parser


@pytest.fixture
def args_parser():
    return create_args_parser()


common_testcases = [
    ("boo", {"boo": 1}, [1]),
    ("$.*", {"boo": 1, "bar": 2}, [1, 2]),
]


@pytest.mark.parametrize(
    "expression, data, expect", common_testcases,
)
def test_parse_json_file_and_extract(
    expression, data, expect, args_parser, tmpdir
):
    json_file_path = Path(tmpdir) / "test_example.json"
    with json_file_path.open("w") as f:
        json.dump(data, f)

    args = args_parser.parse_args([expression, "-f", str(json_file_path)])

    output = StringIO()
    with redirect_stdout(output):
        cli(args)

    output.seek(0, os.SEEK_SET)
    result = json.load(output)
    assert result == expect


@pytest.mark.parametrize("expression, data, expect", common_testcases)
def test_parse_json_from_stdin_and_extract(
    expression, data, expect, args_parser
):
    input_ = StringIO()
    json.dump(data, input_)
    input_.seek(0, os.SEEK_SET)

    args = args_parser.parse_args([expression])

    output = StringIO()
    with redirect_stdout(output), mock.patch.object(sys, "stdin", new=input_):
        cli(args)

    output.seek(0, os.SEEK_SET)
    result = json.load(output)
    assert result == expect


def test_no_json_input_error(args_parser):
    args = args_parser.parse_args(["boo"])
    with pytest.raises(SystemExit) as catched, mock.patch.object(
        sys, "stdin"
    ) as mock_stdin:
        mock_stdin.isatty.return_value = True
        cli(args)

    assert str(catched.value) == "JSON file is needed."


def test_invalid_expression_errror(args_parser):
    args = args_parser.parse_args(["$["])
    with pytest.raises(SystemExit) as catched:
        cli(args)

    assert str(catched.value) == "'$[' is not a valid JSONPath expression."
