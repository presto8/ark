import os
from pathlib import Path
from . import fs
from . import store


class Noah:
    def __init__(self, arkdir):
        self.arkdir = self.resolve_arkdir(arkdir)
        self.store = store.Store(self.arkdir / "store")

    def resolve_arkdir(self, arkdir):
        if arkdir:
            path = arkdir
        elif 'XDG_CONFIG_HOME' in os.environ:
            path = os.path.join(os.environ['XDG_CONFIG_HOME'], 'ark')
        else:
            path = os.path.join(os.environ['HOME'], '.config', 'ark')
        return Path(path)


def backup(noah, pathspec: list[Path]) -> None:
    for path in pathspec:
        scanresults = {x.abspath: x for x in fs.scandepth(path)}

        for abspath, result in scanresults.items():
            fsdir = result.FsDir

            if noah.store.match(*fsdir.time_selector):
                reason = 'have'
            else:
                if noah.store.match(fsdir.abspath, fsdir.b2):
                    reason = "ctime"
                elif noah.store.match(fsdir.abspath):
                    reason = "changed"
                else:
                    reason = "added"
                print(fsdir)
                noah.store.put(fsdir)
            print(f"{reason:<10} {result.abspath}")


    # TODO: binary search based on ctime if performance needed

