from src import store


def test_store_basic(tmp_path):
    s = store.Store(tmp_path)

    assert not s.have("blah")

    s.put("hello.txt", b"hello\n")
    assert s.have("hello.txt")
    assert s.get("hello.txt") == b"hello\n"
