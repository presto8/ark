import attr
import msgpack
import os
from typing import Generator, Optional
from . import crypto


def flatten(input_list: list[str]) -> str:
    return ' '.join([x if ' ' not in x else f'"{x}"' for x in input_list])


def timestamp(path: os.PathLike) -> int:
    return os.lstat(path).st_mtime_ns


@attr.define
class FsEntry:
    path: os.PathLike
    ts: int
    hash: Optional[bytes] = None  # lazy load

    @property
    def abspath(self):
        return os.path.abspath(self.path)

    def read(self):
        raise

    @property
    def selector(self):
        children = sorted([x.abspath for x in self.children]) if isinstance(self, FsDir) else None
        result = [self.abspath, [self.abspath, self.ts, children]]
        if self.hash:
            result.append([self.abspath, self.hash])
        return result


@attr.define
class FsFile(FsEntry):
    def __repr__(self):
        h = self.hash.hex()[:8] if self.hash else "None"
        return f"FsFile({os.path.basename(self.abspath)} {self.ts / 1E9} {h})"

    @staticmethod
    def new(path: os.PathLike):
        ts = timestamp(path)
        return FsFile(path=path, ts=ts)

    def update(self):
        if os.path.islink(self.path):
            contents = os.readlink(self.abspath).encode()
        else:
            contents = open(self.abspath, "rb").read()
        self.hash = crypto.blake2b(contents)

    def read(self):
        return open(self.abspath, "rb").read()


@attr.define
class FsDir(FsEntry):
    files: list[FsFile] = attr.field(factory=list)
    subdirs: list["FsDir"] = attr.field(factory=list)

    def __repr__(self):
        h = self.hash.hex()[:8] if self.hash else "None"
        files = [x for x in self.files]
        # subdirs = flatten([os.path.basename(x.abspath) for x in self.subdirs])
        subdirs = [x for x in self.subdirs]
        extras = f" files={files} subdirs=[{subdirs}]"
        return f"FsDir({self.abspath} {self.ts / 1E9} {h}{extras})"

    @staticmethod
    def new(path: os.PathLike, files: list[FsFile], subdirs: list["FsDir"]):
        try:
            ts = max([x.ts for x in files + subdirs])
        except ValueError:
            ts = timestamp(path)
        return FsDir(path=path, ts=ts, files=files, subdirs=subdirs)

    @property
    def children(self):
        return sorted(self.files + self.subdirs, key=lambda x: x.abspath)

    def update(self):
        for x in self.children:
            x.update()
        if any([x.hash is None for x in self.children]):
            raise
        child_hashes = msgpack.packb(sorted([x.selector for x in self.children]))
        self.hash = crypto.blake2b(child_hashes)

    def read(self):
        return str(self).encode()


@attr.define
class FsCache:
    fsdir_cache: dict[str, FsDir] = {}

    def scanpath(self, *paths) -> Generator[FsDir, None, None]:
        "Scan entire path, store results in cache, and yield depth first to caller."
        for path in paths:
            for entry in scandepth(path):
                self.fsdir_cache[entry.abspath] = entry
                yield entry

    def fsdir(self, path: os.PathLike) -> FsDir:
        """Return ScanEntry for abspath from the cache, retrieving it from disk
        if necessary."""
        abspath = os.path.abspath(path)
        if abspath not in self.fsdir_cache:
            list(self.scanpath(path))  # update cache
        return self.fsdir_cache[abspath]


def scandepth(path: os.PathLike) -> Generator[FsDir, None, None]:
    "Depth-first recursive scan of `path`."
    files, subdirs = [], []
    abspath = os.path.abspath(path)
    for entry in os.scandir(abspath):
        if entry.is_dir(follow_symlinks=False):
            for next_subdir in scandepth(entry):
                yield next_subdir
            # because we are depth first, the last entry will be the original subdir
            subdirs.append(next_subdir)
        else:
            files.append(FsFile.new(entry))
    yield FsDir.new(path=path, files=files, subdirs=subdirs)
