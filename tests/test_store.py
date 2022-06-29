from src import store


class SampleObj:
    def __init__(self, *args):
        self.args = args

    @property
    def selector(self):
        return self.args

    def read(self):
        return b"sample"


def test_store_basic(tmp_path):
    s = store.Store(tmp_path / "store")

    t = SampleObj("/var/mnt/blah.txt", "blah")
    assert not s.have(t)
    s.put(t)
    assert s.have(t)

    s.putb("hello.txt", b"hello\n")
    assert s.getb("hello.txt") == b"hello\n"


def test_match(tmp_path):
    s = store.Store(tmp_path / "store")
    t = SampleObj("/var/mnt/blah.txt", "blah", "foo", "bar")
    result = s.put(t)
    parts = result.split("_")

    return

    m = s.match("blah")
    assert sum(m) == 1
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
