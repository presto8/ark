#!/usr/bin/env python

from protect import nar
from helpers import create_file
from base64 import b16decode
import os
import stat


def xxd_to_bin(s):
    return b16decode(s.replace("\n", "").replace(" ", "").upper())


def test_regular_file(tmp_path):
    path = tmp_path / "world"
    create_file(path, "hello\n")
    serialization = nar.serialise(path)

    expected = xxd_to_bin("""
    0d00 0000 0000 0000 6e69 782d 6172 6368
    6976 652d 3100 0000 0100 0000 0000 0000
    2800 0000 0000 0000 0400 0000 0000 0000
    7479 7065 0000 0000 0700 0000 0000 0000
    7265 6775 6c61 7200 0800 0000 0000 0000
    636f 6e74 656e 7473 0600 0000 0000 0000
    6865 6c6c 6f0a 0000 0100 0000 0000 0000
    2900 0000 0000 0000""")
    assert serialization == expected


def test_executable(tmp_path):
    path = tmp_path / "a-script"
    create_file(path, "echo hello world\n")
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC)
    serialization = nar.serialise(path)

    expected = xxd_to_bin("""
    0d00 0000 0000 0000 6e69 782d 6172 6368
    6976 652d 3100 0000 0100 0000 0000 0000
    2800 0000 0000 0000 0400 0000 0000 0000
    7479 7065 0000 0000 0700 0000 0000 0000
    7265 6775 6c61 7200 0a00 0000 0000 0000
    6578 6563 7574 6162 6c65 0000 0000 0000
    0000 0000 0000 0000 0800 0000 0000 0000
    636f 6e74 656e 7473 1100 0000 0000 0000
    6563 686f 2068 656c 6c6f 2077 6f72 6c64
    0a00 0000 0000 0000 0100 0000 0000 0000
    2900 0000 0000 0000""")
    print(serialization)
    assert serialization == expected


def test_symlink(tmp_path):
    path = tmp_path / "world"
    create_file(path, "hello\n")
    os.chdir(tmp_path)
    os.symlink("world", "mundo")
    serialization = nar.serialise(tmp_path / "mundo")

    expected = xxd_to_bin("""
    0d00 0000 0000 0000 6e69 782d 6172 6368
    6976 652d 3100 0000 0100 0000 0000 0000
    2800 0000 0000 0000 0400 0000 0000 0000
    7479 7065 0000 0000 0700 0000 0000 0000
    7379 6d6c 696e 6b00 0600 0000 0000 0000
    7461 7267 6574 0000 0500 0000 0000 0000
    776f 726c 6400 0000 0100 0000 0000 0000
    2900 0000 0000 0000""")

    assert serialization == expected


def test_directory(tmp_path):
    test_dir = tmp_path / "test_files"
    test_dir.mkdir()
    create_file(test_dir / "thoughts", "when in the course of human events")
    serialization = nar.serialise(test_dir)
    assert serialization == ""
