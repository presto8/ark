import msgpack
from src import crypto
from src import fs
from helpers import create_test_files, create_file
from src.utils import dprint, timestamp


def test_mtime_change(tmp_path):
    testfile = tmp_path / "hello"
    create_file(testfile)

    mtime1 = timestamp(testfile)
    testfile.touch()
    mtime2 = timestamp(testfile)

    assert mtime1 != mtime2


def test_simple_files(tmp_path):
    # directory containing only files (depth=0)
    files = create_test_files(tmp_path, {"world.txt": "world\n", "hello.txt": "hello\n"})
    cache = fs.FsCache()
    fsdir = cache.fsdir(tmp_path)

    assert len(fsdir.children) == files.num_files

    # children must be sorted alphabetically by name
    assert fsdir.children[0].path.name == "hello.txt"
    assert fsdir.children[1].path.name == "world.txt"

    # ts of parent is ctime of the newest file
    assert fsdir.ts >= files.newest_file_ts

    # test hash
    hello, world = fsdir.children
    assert hello.hash is None

    fsdir.update()
    assert hello.hash == crypto.blake2b(b"hello\n")
    assert world.hash == crypto.blake2b(b"world\n")


def test_symlink(tmp_path):
    # add a symlink
    create_test_files(tmp_path, {"hello.txt": "hello\n", "default.txt": "link:hello.txt"})
    fsdir = fs.FsCache().fsdir(tmp_path)

    # hash for default
    default = fsdir.children[0]
    default.update()
    assert default.path.name == "default.txt"
    assert default.hash == crypto.blake2b(b"hello.txt")


def test_nested_dir(tmp_path):
    files = create_test_files(tmp_path, {"hello.txt": "hello\n", "subdir": {"world.txt": "world\n"}})
    cache = fs.FsCache()
    cache.scanpath(tmp_path)

    top = cache.fsdir(tmp_path)

    subdir = cache.fsdir(tmp_path / "subdir")
    subdir.update()
    hello = top.children[0]

    world = subdir.children[0]
    assert world.hash == crypto.blake2b(b"world\n")

    # subdir
    assert len(subdir.children) == 1
    assert subdir.path.name == "subdir"
    assert subdir.ts == world.ts
    assert subdir.hash == crypto.blake2b(msgpack.packb([world.selector]))

    # top
    top.update()
    assert len(top.children) == 2
    assert top.abspath == str(tmp_path)
    assert top.ts == files.newest_file_ts
    assert top.hash == crypto.blake2b(msgpack.packb(sorted([hello.selector, subdir.selector])))


def test_empty_dir(tmp_path):
    fsdir = fs.FsCache().fsdir(tmp_path)
    fsdir.update()
    assert fsdir.hash == crypto.blake2b(msgpack.packb([]))
    # ts of empty dir is the dir's ts
    assert fsdir.ts == timestamp(tmp_path)


def test_broken_link(tmp_path):
    create_test_files(tmp_path, {"hello.txt": "hello\n", "default.txt": "link:hello.txt"})

    hello = tmp_path / "hello.txt"
    hello.unlink()

    fsdir = fs.FsCache().fsdir(tmp_path)
    fsdir.update()

    assert len(fsdir.children) == 1

    # hash for default
    default = fsdir.children[0]
    default.update()
    assert default.path.name == "default.txt"
    assert default.hash == crypto.blake2b(b"hello.txt")
