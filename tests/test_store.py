import pytest
from src import store


def test_store_basic(tmp_path):
    s = store.Store(tmp_path / "store")

    class Test:
        @property
        def selector(self):
            return ["blah"]

    t = Test()
    assert not s.have(t)
    s.put(t)
    assert s.have(t)

    s.putb("hello.txt", b"hello\n")
    assert s.getb("hello.txt") == b"hello\n"


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
