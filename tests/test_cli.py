# Standard Library
import json
import sys

from functools import wraps
from pathlib import Path

# Third Party Library
import pexpect
import pytest

JP = f"{sys.executable} -m jsonpath.cli"

common_testcases = [
    ("boo", {"boo": 1}, [1]),
    ("$.*", {"boo": 1, "bar": 2}, [1, 2]),
]


@pytest.fixture
def spawn():
    ps = []

    @wraps(pexpect.spawn)
    def wrapper(*args, **kwargs):
        p = pexpect.spawn(
            *args,
            logfile=sys.stdout.buffer,
            **kwargs,
        )
        ps.append(p)
        return p

    yield wrapper

    for p in ps:
        p.close()

    sys.stdout.flush()


@pytest.mark.parametrize(
    "expression, data, expect",
    common_testcases,
)
def test_parse_json_file_and_extract(spawn, expression, data, expect, tmpdir):
    json_file_path = Path(tmpdir) / "test_example.json"
    with json_file_path.open("w") as f:
        json.dump(data, f)

    p = spawn(f"{JP} {expression} -f {json_file_path}")
    p.expect_exact(json.dumps(expect, indent=2).split("\n"))
    p.wait()
    assert p.exitstatus == 0


@pytest.mark.parametrize("expression, data, expect", common_testcases)
def test_parse_json_from_stdin_and_extract(spawn, expression, data, expect, tmpdir):
    json_file_path = Path(tmpdir) / "test_example.json"
    with json_file_path.open("w") as f:
        json.dump(data, f)

    p = spawn(
        "/bin/bash",
        ["-c", f"cat {json_file_path} | {JP} {expression}"],
    )
    p.expect_exact(json.dumps(expect, indent=2).split("\n"))
    p.wait()
    assert p.exitstatus == 0


def test_no_json_input_error(spawn):
    p = spawn(f"{JP} boo")
    p.expect("JSON file is needed.")
    p.wait()
    assert p.exitstatus == 1


def test_invalid_expression_errror(spawn):
    p = spawn(f"{JP} []")
    p.expect_exact("'[]' is not a valid JSONPath expression.")
    p.wait()
    assert p.exitstatus == 1
