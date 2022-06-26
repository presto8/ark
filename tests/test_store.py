import pytest
from src import store


class SampleObj:
    def __init__(self, *args):
        self.args = args

    @property
    def selector(self):
        return self.args


def test_store_basic(tmp_path):
    s = store.Store(tmp_path / "store")

    t = SampleObj("blah")
    assert not s.have(t)
    s.put(t)
    assert s.have(t)

    s.putb("hello.txt", b"hello\n")
    assert s.getb("hello.txt") == b"hello\n"


def test_match(tmp_path):
    s = store.Store(tmp_path / "store")
    t = SampleObj("blah", "foo", "bar")
    result = s.put(t)
    parts = result.split("_")

    m = s.match("blah")
    assert len(m) == 1
    matching = m[0]
    assert parts[0] in matching

    m = s.match("blah", "foo")
    assert len(m) == 1
    matching = m[0]
    assert parts[0] in matching
    assert parts[1] in matching

    m = s.match("blah", "foo", "bar")
    assert len(m) == 1
    matching = m[0]
    assert parts[0] in matching
    assert parts[1] in matching
    assert parts[2] in matching


def test_base64():
    assert store.b64e("") == ""
    assert store.b64e("f") == "Zg=="
    assert store.b64e("fo") == "Zm8="
    assert store.b64e("foo") == "Zm9v"
    assert store.b64e("foob") == "Zm9vYg=="
    assert store.b64e("fooba") == "Zm9vYmE="
    assert store.b64e("foobar") == "Zm9vYmFy"

    assert store.b64d("") == b""
    assert store.b64d("Zg==") == b"f"
    assert store.b64d("Zm8=") == b"fo"
    assert store.b64d("Zm9v") == b"foo"
    assert store.b64d("Zm9vYg==") == b"foob"
    assert store.b64d("Zm9vYmE=") == b"fooba"
    assert store.b64d("Zm9vYmFy") == b"foobar"
