#!/usr/bin/env python

#from protect import nar
from helpers import create_file
from base64 import b16decode
import os
import stat


def xxd_to_bin(s):
    return b16decode(s.replace("\n", "").replace(" ", "").upper())


def create_test_files(tmp_path):
    foo = tmp_path / "foo"
    create_file(foo / "hello.txt", "hello, world\n")
    bar = foo / "bar"
    create_file(bar / "hola.txt", "hola, mundo\n")
    zzz = foo / "zzz"
    os.symlink("bar", zzz)


def test_regular_file(tmp_path):
    create_test_files(tmp_path)
    print(tmp_path)
    assert False
