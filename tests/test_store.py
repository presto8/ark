from src import store


def test_store_basic(tmp_path):
    s = store.Store(tmp_path / "store")

    assert not s.have("blah")

    s.putb("hello.txt", b"hello\n")
    assert s.have("hello.txt")
    assert s.getb("hello.txt") == b"hello\n"


def test_base64():
    assert store.b64e("") == ""
    assert store.b64e("f") == "Zg=="
    assert store.b64e("fo") == "Zm8="
    assert store.b64e("foo") == "Zm9v"
    assert store.b64e("foob") == "Zm9vYg=="
    assert store.b64e("fooba") == "Zm9vYmE="
    assert store.b64e("foobar") == "Zm9vYmFy"

    assert store.b64d("") == ""
    assert store.b64d("Zg==") == "f"
    assert store.b64d("Zm8=") == "fo"
    assert store.b64d("Zm9v") == "foo"
    assert store.b64d("Zm9vYg==") == "foob"
    assert store.b64d("Zm9vYmE=") == "fooba"
    assert store.b64d("Zm9vYmFy") == "foobar"
