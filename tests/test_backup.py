import os
from src import fs
from src.store import Store
from helpers import create_test_files
from pathlib import Path


def test_simple_backup(tmp_path):
    # directory containing only files (depth=0)
    foo = tmp_path / "foo"
    create_test_files(foo, {"world.txt": "world\n", "hello.txt": "hello\n"})
    parent = fs.get_parent(foo)

    store = Store(Path(tmp_path / "store"))

    for child in parent.children:
        store.put(child)

    for child in parent.children:
        assert store.have(child)


def test_ctime_change(tmp_path):
    create_test_files(tmp_path, {"world.txt": "world\n"})

    parent = fs.get_parent(tmp_path)
    child = parent.children[0]

    store = Store(Path(tmp_path / "store"))
    store.put(child)
    assert store.have(child)

    # change time
    child.path.touch()

    parent = fs.get_parent(tmp_path)
    child = parent.children[0]
    assert not store.have(child)


def test_subdirs_backup(tmp_path):
    # directory containing only files (depth=0)
    foo = tmp_path / "foo"
    create_test_files(foo, {"hello.txt": "hello\n", "subdir": {"world.txt": "world\n"}})
    parent = fs.get_parent(tmp_path)

    store = Store(Path(tmp_path / "store"))
    store.put(parent)
    assert store.have(parent)

    # timestamp change
    hello = parent.children[0].children[0]
    hello.path.touch()
    parent = fs.get_parent(tmp_path)
    hello = parent.children[0].children[0]
    assert not store.have(parent)
    store.put(parent)

    # filename change
    foo = parent.children[0]
    hello.path.rename(foo.path / "hola.txt")
    parent = fs.get_parent(tmp_path)
    assert not store.have(parent)
