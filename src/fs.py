import msgpack
import os
import platform
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from . import crypto


@dataclass
class ArkObject:
    @property
    def path(self):
        pass

    @property
    def arkhash(self):
        if self.is_parent:
            return None
        payload = [self.path.name, self.ctime_ns, self.b2]
        return crypto.blake2b(msgpack.dumps(payload))


@dataclass
class FsEntry:
    """FsEntry captures a moment in time of a filesystem entry. The ctime and
    hash are computed once and then cached after that. If the underling
    filesystem changes, the cached values will be returned. To detect
    filesystem changes, create a new FsEntry object."""
    path: Path

    # abstract methods

    def ctime_ns(self) -> int:
        raise

    def pth(self):
        "path-time-hash"
        raise

    def ptch(self):
        "path-time-contents-hash"
        raise


@dataclass
class FsChild(FsEntry):
    def __post_init__(self):
        self._b2 = None

    @property
    def ctime_ns(self) -> int:
        # pathlib caches this after this first call
        return self.path.stat().st_ctime_ns

    @property
    def b2(self):
        if self._b2 is None:
            self._update()
        return self._b2

    def _update(self):
        if self.path.is_symlink():
            contents = str(self.path.readlink()).encode()
        else:
            contents = open(self.path, "rb").read()
        self._b2 = crypto.blake2b(contents)

    @property
    def pth(self):
        return crypto.blake2b(msgpack.packb([self.path.name, self.ctime_ns]))

    @property
    def ptch(self):
        return crypto.blake2b(msgpack.packb([self.path.name, self.ctime_ns, self.b2]))


@dataclass
class FsParent(FsEntry):
    hostname: str
    fsid: str
    children: list[FsEntry] = field(default_factory=list)
    loaded: bool = False

    @property
    def ctime_ns(self) -> int:
        return max([x.ctime_ns for x in self.children])

    @property
    def pth(self) -> bytes:
        child_vals = sorted([x.pth for x in self.children])
        return crypto.blake2b(msgpack.packb([self.path.name, self.ctime_ns, child_vals]))

    @property
    def ptch(self) -> bytes:
        child_vals = sorted([x.ptch for x in self.children])
        return crypto.blake2b(msgpack.packb([self.path.name, self.ctime_ns, child_vals]))


def get_parent(path, max_depth=-1) -> FsParent:
    hostname = platform.node()
    fsid = 'TODO'
    children = []
    next_child: FsEntry
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            if max_depth == 0:  # stop recursion
                next_child = FsParent(hostname=hostname, fsid=fsid, path=Path(entry))
            else:
                next_child = get_parent(entry, max_depth=max_depth - 1)
        else:
            next_child = FsChild(path=Path(entry))
        children.append(next_child)

    children.sort(key=lambda x: x.path.name)
    return FsParent(hostname=hostname, fsid=fsid, path=Path(path), children=children, loaded=True)
