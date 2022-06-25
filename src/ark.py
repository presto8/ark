from pathlib import Path
from . import fs


def backup(pathspec: list[Path]) -> None:
    for path in pathspec:
        parent = fs.get_parent(path)
        print(f"{path}: {len(parent.children)}")
