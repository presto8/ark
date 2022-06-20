import os

from types import SimpleNamespace

from src import fs
from helpers import create_file


def create_test_files(tmp_path):
    foo = tmp_path / "foo"
    create_file(foo / "hello.txt", "hello, world\n")
    bar = foo / "bar"
    create_file(bar / "hola.txt", "hola, mundo\n")
    zzz = foo / "zzz"
    os.symlink("bar", zzz)

    return SimpleNamespace(foo=foo, bar=bar, zzz=zzz)


def test_regular_file(tmp_path):
    files = create_test_files(tmp_path)
    print(files.foo.name)

    for f in fs.scan_fs(files.foo):
        print(f)
