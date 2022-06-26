import os
from os.path import abspath
import msgpack
from types import SimpleNamespace
from src import crypto
from src import fs
from helpers import create_test_files


def test_simple_files(tmp_path):
    # directory containing only files (depth=0)
    create_test_files(tmp_path, {"world.txt": "world\n", "hello.txt": "hello\n"})
    parent = fs.get_parent(tmp_path)

    assert len(parent.children) == 2
    # children must be sorted alphabetically by name
    assert parent.children[0].path.name == "hello.txt"
    assert parent.children[1].path.name == "world.txt"
    # ctime_ns of parent is max(ctime_ns) of children
    assert parent.ctime_ns == (tmp_path / "world.txt").stat().st_ctime_ns


def test_symlink(tmp_path):
    # add a symlink
    create_test_files(tmp_path, {"hello.txt": "hello\n", "default.txt": "link:hello.txt"})
    parent = fs.get_parent(tmp_path)

    assert len(parent.children) == 2
    # ctime_ns of parent is ctime_ns of the newest child
    assert parent.ctime_ns == os.lstat(tmp_path / "default.txt").st_ctime_ns

    # selector for hello
    hello = parent.children[1]
    assert hello.path.name == "hello.txt"
    hello_b2 = crypto.blake2b(b"hello\n")
    hello_selector = [abspath(hello.path), hello.path.stat().st_ctime_ns, hello_b2]
    assert hello.selector == hello_selector

    # ptch for child 1
    default = parent.children[0]
    assert default.path.name == "default.txt"
    link_b2 = crypto.blake2b(b"hello.txt")
    default_selector = [abspath(default.path), default.path.stat().st_ctime_ns, link_b2]
    assert default.selector == default_selector

    joined = sorted([hello_b2, link_b2])

    parent_selector = [abspath(tmp_path), parent.ctime_ns, joined]
    # assert parent.selector == parent_selector


def test_b2(tmp_path):
    create_test_files(tmp_path, {"hello.txt": "hello\n", "world.txt": "world\n", "default.txt": "link:world.txt"})
    parent = fs.get_parent(tmp_path)

    assert parent.children[0].path.name == "default.txt"

    world_b2 = crypto.blake2b(open(tmp_path / "world.txt", "rb").read())
    assert parent.children[-1].b2 == world_b2


def test_selector_file(tmp_path):
    create_test_files(tmp_path, {"hello.txt": "hello\n", "world.txt": "world\n", "default.txt": "link:world.txt"})
    parent = fs.get_parent(tmp_path)

    # child 1 selector
    c1 = parent.children[1]
    assert c1.path.name == "hello.txt"
    c1_b2 = crypto.blake2b(b"hello\n")
    assert c1.b2 == c1_b2
    selector = [abspath(c1.path), c1.path.stat().st_ctime_ns, c1_b2]
    assert c1.selector == selector


def test_selector_dir(tmp_path):
    create_test_files(tmp_path, {"hello.txt": "hello\n"})
    parent = fs.get_parent(tmp_path)

    # child 0 selector
    c0 = parent.children[0]
    assert c0.path.name == "hello.txt"
    c0_ctime = c0.path.stat().st_ctime_ns
    c0_b2 = crypto.blake2b(b"hello\n")

    child_b2s = crypto.blake2b(msgpack.packb([c0_b2]))
    assert parent.selector == [abspath(parent.path), c0_ctime, child_b2s]


def test_selector_simple_dir(tmp_path):
    create_test_files(tmp_path, {"hello.txt": "hello\n", "world.txt": "world\n"})
    parent = fs.get_parent(tmp_path)

    # selector for child 0
    c0 = parent.children[0]
    assert c0.path.name == "hello.txt"
    c0_b2 = crypto.blake2b(b"hello\n")
    c0_selector = [abspath(c0.path), c0.path.stat().st_ctime_ns, c0_b2]
    assert c0.selector == c0_selector

    # selector for child 1
    c1 = parent.children[1]
    assert c1.path.name == "world.txt"
    c1_b2 = crypto.blake2b(b"world\n")
    c1_ctime = c1.path.stat().st_ctime_ns
    assert c1.selector == [abspath(c1.path), c1_ctime, c1_b2]

    joined = [c0_b2, c1_b2]
    joined.sort()
    children_b2 = crypto.blake2b(msgpack.packb(joined))

    parent_selector = [abspath(tmp_path), c1_ctime, children_b2]
    assert parent.selector == parent_selector


def test_selector_timestamp_change(tmp_path):
    create_test_files(tmp_path, {"hello.txt": "hello\n", "world.txt": "world\n"})
    parent = fs.get_parent(tmp_path)

    sel1 = parent.selector
    assert sel1 is not None

    hello = parent.children[0]
    assert hello.path.name == "hello.txt"
    hello.path.touch()

    parent = fs.get_parent(tmp_path)
    print(parent.selector)
    print(sel1)
    # assert parent.selector != sel1


def test_selector_deep_dir(tmp_path):
    create_test_files(tmp_path, {"hello.txt": "hello\n", "subdir": {"world.txt": "world\n"}})
    parent = fs.get_parent(tmp_path)

    assert len(parent.children) == 2

    # selector for "hello.txt"
    hello = parent.children[0]
    assert hello.path.name == "hello.txt"
    hello_b2 = crypto.blake2b(b"hello\n")
    assert hello.selector == [abspath(hello.path), hello.path.stat().st_ctime_ns, hello_b2]

    # selector for "world.txt"
    world = parent.children[1].children[0]
    assert world.path.name == "world.txt"
    world_b2 = crypto.blake2b(b"world\n")
    world_ctime = world.path.stat().st_ctime_ns
    assert world.selector == [abspath(world.path), world_ctime, world_b2]

    # selector for "subdir"
    subdir = parent.children[1]
    assert subdir.path.name == "subdir"
    subdir_child_b2s = crypto.blake2b(msgpack.packb([world_b2]))
    assert subdir.selector == [abspath(subdir.path), world_ctime, subdir_child_b2s]

    # selector for parent
    child_b2s = crypto.blake2b(msgpack.packb(sorted([hello_b2, subdir_child_b2s])))
    parent_selector = [abspath(parent.path), world_ctime, child_b2s]
    assert parent.selector == parent_selector


def test_stop_recursion(tmp_path):
    create_test_files(tmp_path, {"hello.txt": "hello\n", "subdir": {"world.txt": "world\n", "anothersub": {"hola.txt": "hola\n"}}})

    parent = fs.get_parent(tmp_path, max_depth=0)
    assert len(parent.children) == 2
    file_children = [x for x in parent.children if isinstance(x, fs.FsFile)]
    assert len(file_children) == 1
    assert parent.children[1].loaded is False
