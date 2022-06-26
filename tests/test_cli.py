import contextlib
import io
import sys
from src import cli
from types import SimpleNamespace


@contextlib.contextmanager
def captured_output():
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def run_cli(args):
    with captured_output() as (out, err):
        try:
            cli.main(args)
        except SystemExit:
            pass

        return SimpleNamespace(stdout=out.getvalue(), stderr=err.getvalue())


def test_help():
    result = run_cli("--help".split())
    assert "Ark by Preston Hunt" in result.stdout
