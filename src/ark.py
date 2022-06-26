from pathlib import Path
from . import fs
from . import store


S = store.Store(Path("/tmp/store"))


def backup(pathspec: list[Path]) -> None:
    for path in pathspec:
        parent = fs.get_parent(path)
        for m in S.match(parent.selector, 1):
            print(m)
        if S.have(parent.selector):
            reason = "have"
        else:
            S.put(parent.selector)
            reason = "added"
        print(f"{path}: {reason}")
