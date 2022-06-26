import contextlib
import io
from os.path import abspath, stat
import os
import sys
import time
from src import cli
from types import SimpleNamespace
from helpers import create_test_files


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


def test_no_args():
    result = run_cli("".split())
    assert "Ark by Preston Hunt" in result.stdout


def test_backup(tmp_path):
    create_test_files(tmp_path, {"hello": "hola\n", "world": "mundo\n"})
    result = run_cli(["backup", abspath(tmp_path)])
    assert 'added' in result.stdout

    result = run_cli(["backup", abspath(tmp_path)])
    assert 'have' in result.stdout

    hello = tmp_path / "hello"
    with open(hello, "wt") as f:
        f.write('blahblah')

    result = run_cli(["backup", abspath(tmp_path)])
    assert 'changed' in result.stdout

    # ctime1 = os.stat(hello).st_ctime_ns
    # hello.touch()
    # # wait for the fs to notice the ctime change
    # while os.stat(hello).st_ctime_ns == ctime1:
    #     time.sleep(0.001)
    # result = run_cli(["backup", abspath(tmp_path)])
    # assert 'ctime' in result.stdout


# def test_not_a_directory():
#     result = run_cli("backup /dev/null".split())
#     assert "arguments are required" in result.stderr
