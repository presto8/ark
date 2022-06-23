from src import store


def test_store_init():
    s = store.Store()
    assert s
