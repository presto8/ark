import os
import msgpack
from types import SimpleNamespace
from src import crypto
from src import fs
from helpers import create_file


def create_test_files(dir_path, structure):
    for name, value in structure.items():
        if isinstance(value, str):
            if value.startswith("link:"):
                # create a symlink
                os.symlink(value[5:], dir_path / name)
            else:
                # create a file
                create_file(dir_path / name, value)
        elif isinstance(value, dict):
            # directory - recurse
            create_test_files(dir_path / name, value)
        else:
            # error
            raise


def test_simple_files(tmp_path):
    # directory containing only files (depth=0)
    create_test_files(tmp_path, {"world.txt": "world\n", "hello.txt": "hello\n"})
    parent = fs.get_parent(tmp_path)

    assert len(parent.children) == 2
    # children must be sorted alphabetically by name
    assert parent.children[0].path.name == "hello.txt"
    assert parent.children[1].path.name == "world.txt"
    assert parent.tpch is None
    # ctime_ns of parent is max(ctime_ns) of children
    assert parent.ctime_ns == (tmp_path / "world.txt").stat().st_ctime_ns


def test_symlink(tmp_path):
    # add a symlink
    create_test_files(tmp_path, {"hello.txt": "hello\n", "world.txt": "world\n", "default.txt": "link:world.txt"})
    parent = fs.get_parent(tmp_path)

    assert len(parent.children) == 3
    assert parent.tpch is None
    # ctime_ns of parent is max(ctime_ns) of children
    assert parent.ctime_ns == os.lstat(tmp_path / "default.txt").st_ctime_ns


def test_b2(tmp_path):
    create_test_files(tmp_path, {"hello.txt": "hello\n", "world.txt": "world\n", "default.txt": "link:world.txt"})
    parent = fs.get_parent(tmp_path)
    parent.update()

    assert parent.children[0].path.name == "default.txt"

    world_b2 = crypto.blake2b(open(tmp_path / "world.txt", "rb").read())
    assert parent.children[-1].b2 == world_b2


def test_msgpack_file(tmp_path):
    create_test_files(tmp_path, {"hello.txt": "hello\n", "world.txt": "world\n", "default.txt": "link:world.txt"})
    parent = fs.get_parent(tmp_path)
    parent.update()

    # msgpack and tpch for child 1
    c0 = parent.children[1]
    assert c0.path.name == "hello.txt"
    c0.ctime_ns = 100
    c0_b2 = crypto.blake2b(b"hello\n")
    assert c0.b2 == c0_b2
    payload = ["hello.txt", 100, c0_b2]
    expected = msgpack.packb(payload)
    assert c0._msgpack == expected
    assert c0.tpch == crypto.blake2b(expected)


def test_tpch_simple_dir(tmp_path):
    create_test_files(tmp_path, {"hello.txt": "hello\n", "world.txt": "world\n"})
    parent = fs.get_parent(tmp_path)
    parent.update()

    # tpch for child 0
    c0 = parent.children[0]
    c0.ctime_ns = 100
    c0_b2 = crypto.blake2b(b"hello\n")
    c0_tpch = crypto.blake2b(msgpack.packb(["hello.txt", 100, c0_b2]))
    assert c0.tpch == c0_tpch

    # tpch for child 1
    c1 = parent.children[1]
    c1.ctime_ns = 200
    c1_b2 = crypto.blake2b(b"world\n")
    c1_tpch = crypto.blake2b(msgpack.packb(["world.txt", 200, c1_b2]))
    assert c1.tpch == c1_tpch

    joined = [c0_tpch, c1_tpch]
    joined.sort()

    parent_tpch = crypto.blake2b(msgpack.packb([tmp_path.name, 200, joined]))
    assert parent_tpch == parent.tpch


def test_tpch_timestamp_change(tmp_path):
    create_test_files(tmp_path, {"hello.txt": "hello\n", "world.txt": "world\n"})
    parent = fs.get_parent(tmp_path)
    parent.update()

    tpch1 = parent.tpch
    assert parent.tpch is not None

    parent.children[1].ctime_ns = 200
    assert parent.tpch != tpch1


def test_tpch_deep_dir(tmp_path):
    create_test_files(tmp_path, {"hello.txt": "hello\n", "subdir": {"world.txt": "world\n"}})
    parent = fs.get_parent(tmp_path)
    parent.update()

    assert len(parent.children) == 2

    # tpch for child 0
    c0 = parent.children[0]
    c0.ctime_ns = 100
    c0_b2 = crypto.blake2b(b"hello\n")
    c0_tpch = crypto.blake2b(msgpack.packb(["hello.txt", 100, c0_b2]))
    assert c0.tpch == c0_tpch

    # tpch for child 1
    c1 = parent.children[1].children[0]
    c1.ctime_ns = 200
    c1_b2 = crypto.blake2b(b"world\n")
    c1_tpch = crypto.blake2b(msgpack.packb(["world.txt", 200, c1_b2]))
    assert c1.tpch == c1_tpch

    # tpch for subdir
    s0 = parent.children[1]
    s0_tpch = crypto.blake2b(msgpack.packb(["subdir", 200, [c1_tpch]]))
    assert s0.tpch == s0_tpch

    joined = [c0_tpch, c1_tpch]
    joined.sort()
