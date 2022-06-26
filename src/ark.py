from pathlib import Path
from . import fs
from . import store


S = store.Store(Path("/tmp/store"))


def backup(pathspec: list[Path]) -> None:
    for path in pathspec:
        parent = fs.get_parent(path)

        if S.have(parent):
            reason = "have"
        else:
            if S.match(parent.abspath, parent.b2):
                reason = "ctime"
            elif S.match(parent.abspath):
                reason = "changed"
            else:
                reason = "added"
            S.put(parent)

        print(f"{path}: {reason}")

        for m in S.match(parent.abspath):
            print(m)
