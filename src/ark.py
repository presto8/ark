import os
from src import fs
from src import store
from src import utils


class Noah:
    def __init__(self, safedir):
        self.safedir = self.resolve_arkdir(safedir)
        self.store = store.Store(os.path.join(self.safedir, "store"))
        self.fs = fs.FsCache()

    def resolve_arkdir(self, safedir) -> os.PathLike:
        if safedir:
            path = safedir
        elif 'XDG_CONFIG_HOME' in os.environ:
            path = os.path.join(os.environ['XDG_CONFIG_HOME'], 'safe')
        else:
            path = os.path.join(os.environ['HOME'], '.config', 'safe')
        return os.path.abspath(path)


def backup(noah, pathspec: list[os.PathLike]) -> None:
    for fsdir in noah.fs.scanpath(*pathspec):
        mpath, mtime = noah.store.match(fsdir.selector)
        if mtime:
            reason = 'unchanged'
        else:
            fsdir.update()
            mpath, mtime, mhash = noah.store.match(fsdir.selector)
            if mhash == 0:
                reason = 'updated'
            else:
                reason = 'ts'
            noah.store.put(fsdir)
        print(f"{reason:<10} {fsdir.abspath}")

    # TODO: binary search based on ctime if performance needed


def init(noah):
    print("TODO: init")


def info(noah):
    print("TODO: info")
