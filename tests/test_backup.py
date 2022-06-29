from src import fs
from src.store import Store
from helpers import create_test_files
from pathlib import Path


def test_simple_backup(tmp_path):
    # directory containing only files (depth=0)
    foo = tmp_path / "foo"
    create_test_files(foo, {"world.txt": "world\n", "hello.txt": "hello\n"})

    parent = fs.FsCache().fsdir(tmp_path)
    parent.update()

    store = Store(Path(tmp_path / "store"))

    for child in parent.children:
        store.put(child)

    for child in parent.children:
        assert store.have(child)


def test_time_change(tmp_path):
    create_test_files(tmp_path, {"world.txt": "world\n"})

    parent = fs.FsCache().fsdir(tmp_path)
    parent.update()
    child = parent.children[0]

    store = Store(Path(tmp_path / "store"))
    store.put(child)
    assert store.have(child)

    # simulate time change

    child = parent.children[0]
    child.ts += 1

    assert not store.have(child)


def test_subdirs_backup(tmp_path):
    # directory containing only files (depth=0)
    foo = tmp_path / "foo"
    create_test_files(foo, {"hello.txt": "hello\n", "subdir": {"world.txt": "world\n"}})
    parent = fs.FsCache().fsdir(tmp_path)
    parent.update()

    store = Store(Path(tmp_path / "store"))
    store.put(parent)
    assert store.have(parent)

    # timestamp change
    hello = parent.children[0].children[0]
    hello.ts += 100
    parent.update()
    hello = parent.children[0].children[0]
    assert not store.have(parent)
    store.put(parent)

    return

    # filename change
    Path(hello.path).rename(foo / "hola.txt")
    parent = fs.FsCache().fsdir(tmp_path)
    parent.update()
    assert not store.have(parent)
