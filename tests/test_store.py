from src import store


def test_store_basic(tmp_path):
    s = store.Store(tmp_path / "store")

    assert not s.have("blah")

    s.putb("hello.txt", b"hello\n")
    assert s.have("hello.txt")
    assert s.getb("hello.txt") == b"hello\n"
