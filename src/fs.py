import attr
import msgpack
import os
import platform
from pathlib import Path
from typing import Generator
from . import crypto


def flatten(input_list: list[str]) -> str:
    return ' '.join([x if ' ' not in x else f'"{x}"' for x in input_list])


@attr.define
class FsEntry:
    """FsEntry captures a moment in time of a filesystem entry. The ctime and
    hash are computed once and then cached after that. If the underling
    filesystem changes, the cached values will be returned. To detect
    filesystem changes, create a new FsEntry object."""
    path: Path
    _b2: bytes = b""

    def __repr__(self):
        ctime = int(self.ctime_ns / 1E9)
        b2 = self._b2.hex()[:8] if self._b2 else "None"
        cls = self.__class__.__name__
        files = flatten([os.path.basename(x.abspath) for x in self.files])
        subdirs = flatten([os.path.basename(x.abspath) for x in self.subdirs])
        return f"{cls}({ctime} {b2} {self.abspath} files=[{files}] subdirs=[{subdirs}])"

    @property
    def selector(self):
        return [self.abspath, self.ctime_ns, self.b2]

    @property
    def time_selector(self):
        return [self.abspath, self.ctime_ns]

    @property
    def hash_selector(self):
        return [self.abspath, self.ctime_ns, self.b2]

    @property
    def abspath(self):
        return os.path.abspath(self.path)

    @property
    def b2(self):
        if not self._b2:
            self._update_b2()
        return self._b2

    # abstract methods

    def ctime_ns(self) -> int:  # pragma: no cover
        raise

    def _update_b2(self) -> bytes:  # pragma: no cover
        raise

    @staticmethod
    def new(entry: os.DirEntry):
        factory = FsDir if entry.is_dir(follow_symlinks=False) else FsFile
        return factory(path=Path(entry))


@attr.define
class FsFile(FsEntry):
    def __repr__(self):
        return f"FsFile({self._b2.hex()[:8]} {self.abspath})"

    @property
    def ctime_ns(self) -> int:
        return self.path.stat(follow_symlinks=False).st_ctime_ns

    def _update_b2(self):
        if self.path.is_symlink():
            contents = str(self.path.readlink()).encode()
        else:
            contents = open(self.path, "rb").read()
        self._b2 = crypto.blake2b(contents)


@attr.define
class FsDir(FsEntry):
    # hostname: str
    # fsid: str
    files: list[FsFile] = attr.field(factory=list)
    subdirs: list["FsDir"] = attr.field(factory=list)
    loaded: bool = False

    def __repr__(self):
        return super().__repr__()

    # @property
    # def loaded(self) -> bool:
    #     return self.ctime_ns != 0

    @property
    def children(self):
        return sorted(self.files + self.subdirs, key=lambda x: x.abspath)

    @property
    def ctime_ns(self) -> int:
        children_ctime_ns = [x.ctime_ns for x in self.children]
        if not children_ctime_ns:
            return 0
        return max(children_ctime_ns)

    def _update_b2(self):
        for x in self.children:
            print(x, x.b2.hex()[:8])
        if any([not x.b2 for x in self.children]):
            raise
        child_b2s = msgpack.packb(sorted([x.b2 for x in self.children]))
        self._b2 = crypto.blake2b(child_b2s)


@attr.define
class ScanResult:
    abspath: str
    ctime_ns: int
    files: list[os.DirEntry]
    subdirs: list[os.DirEntry]

    def __repr__(self):
        files = flatten([x.name for x in self.files])
        subdirs = flatten([x.name for x in self.subdirs])
        ctime = int(self.ctime_ns / 1E9)
        return f'ScanResult("{self.abspath}" {ctime} files=[{files}] subdirs=[{subdirs}])'

    @property
    def FsDir(self) -> FsDir:
        files = [FsEntry.new(x) for x in self.files]
        subdirs = [FsEntry.new(x) for x in self.subdirs]
        return FsDir(path=Path(self.abspath), files=files, subdirs=subdirs, loaded=True)


def scan_worker(path, depth_first=True) -> Generator[ScanResult, None, None]:
    ctime_ns = os.lstat(path).st_ctime_ns
    files, subdirs = [], []
    for entry in os.scandir(path):
        subdirs.append(entry) if entry.is_dir(follow_symlinks=False) else files.append(entry)
    result = ScanResult(abspath=os.path.abspath(path), ctime_ns=ctime_ns, files=files, subdirs=subdirs)
    if not depth_first:
        yield result
    for entry in result.subdirs:
        for subdir in scan_worker(entry.path, depth_first=depth_first):
            yield subdir
            result.ctime_ns = max(result.ctime_ns, subdir.ctime_ns)
    if depth_first:
        print('yielding', result)
        yield result


def scandepth(path) -> Generator[ScanResult, None, None]:
    "Depth-first recursive scan of `path`."
    yield from scan_worker(path, depth_first=True)


def scanbreadth(path) -> Generator[ScanResult, None, None]:
    "Breadth-first recursive scan of `path`."
    yield from scan_worker(path, depth_first=False)


def get_parent(path, max_depth=-1) -> FsDir:
    files, subdirs = [], []
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            if max_depth == 0:  # stop recursion
                subdirs.append(FsDir(path=Path(entry)))
            else:
                subdirs.append(get_parent(entry, max_depth=max_depth - 1))
        else:
            files.append(FsFile(path=Path(entry)))

    files.sort(key=lambda x: x.abspath)
    subdirs.sort(key=lambda x: x.abspath)

    return FsDir(path=Path(path), files=files, subdirs=subdirs, loaded=True)
