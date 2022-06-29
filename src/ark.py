import os
from . import fs
from . import store


class Noah:
    def __init__(self, arkdir):
        self.arkdir = self.resolve_arkdir(arkdir)
        self.store = store.Store(os.path.join(self.arkdir, "store"))
        self.fs = fs.FsCache()

    def resolve_arkdir(self, arkdir) -> os.PathLike:
        if arkdir:
            path = arkdir
        elif 'XDG_CONFIG_HOME' in os.environ:
            path = os.path.join(os.environ['XDG_CONFIG_HOME'], 'ark')
        else:
            path = os.path.join(os.environ['HOME'], '.config', 'ark')
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
