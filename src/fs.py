import attr
import msgpack
import os
import platform
from pathlib import Path
from typing import Optional
from . import crypto


@attr.define
class FsEntry:
    """FsEntry captures a moment in time of a filesystem entry. The ctime and
    hash are computed once and then cached after that. If the underling
    filesystem changes, the cached values will be returned. To detect
    filesystem changes, create a new FsEntry object."""
    path: Path
    _b2: bytes = b""

    @property
    def selector(self):
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


@attr.define
class FsFile(FsEntry):
    @property
    def ctime_ns(self) -> int:
        # pathlib caches this after this first call
        return self.path.stat().st_ctime_ns

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
    children: list[FsEntry] = attr.field(factory=list)
    loaded: bool = False

    @property
    def ctime_ns(self) -> int:
        if not self.children:
            return 0
        return max([x.ctime_ns for x in self.children])

    def _update_b2(self):
        child_b2s = msgpack.packb(sorted([x.b2 for x in self.children]))
        self._b2 = crypto.blake2b(child_b2s)


def get_parent(path, max_depth=-1) -> FsDir:
    children = []
    next_child: FsEntry
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            if max_depth == 0:  # stop recursion
                next_child = FsDir(path=Path(entry))
            else:
                next_child = get_parent(entry, max_depth=max_depth - 1)
        else:
            next_child = FsFile(path=Path(entry))
        children.append(next_child)

    children.sort(key=lambda x: x.path.name)
    return FsDir(path=Path(path), children=children, loaded=True)
