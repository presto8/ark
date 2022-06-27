import os
from pathlib import Path
from typing import Generator
from . import fs
from . import store


S = store.Store(Path("/tmp/store"))


def scantree_depth_first(path) -> Generator[tuple[str, list[os.DirEntry]], None, None]:
    entries = list(os.scandir(path))
    for entry in entries:
        if entry.is_dir():
            yield from scantree_depth_first(entry.path)
    yield path, entries


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
