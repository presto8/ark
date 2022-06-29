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
    s.put(t)

    m = s.match(["blah"])
    assert m == [1]

    m = s.match(["blah", "foo"])
    assert m == [1, 1]

    m = s.match(["blah", "foo", "bar"])
    assert m == [1, 1, 1]

    m = s.match(["blah", "tad", "bar"])
    assert m == [1, 0, 1]
