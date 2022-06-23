import msgpack
import os
import platform
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional
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
    path: Path


@dataclass
class FsChild(FsEntry):
    ctime_ns: Optional[int] = None
    b2: Optional[bytes] = None

    def update(self, ctime_ns=True, b2=True):
        if ctime_ns:
            self.ctime_ns = self.path.stat(follow_symlinks=False).st_ctime_ns
        if b2:
            if self.path.is_symlink():
                contents = str(self.path.readlink()).encode()
            else:
                contents = open(self.path, "rb").read()
            self.b2 = crypto.blake2b(contents)

    @property
    def _msgpack(self):
        return msgpack.packb([self.path.name, self.ctime_ns, self.b2])

    @property
    def tpch(self):
        if not self.b2:
            return None
        return crypto.blake2b(self._msgpack)


@dataclass
class FsParent(FsEntry):
    hostname: str
    fsid: str
    children: list[FsEntry] = field(default_factory=list)
    loaded: bool = False

    @property
    def ctime_ns(self) -> Optional[int]:
        try:
            return max([x.ctime_ns for x in self.children])
        except TypeError:
            return None

    @property
    def tpch(self) -> Optional[bytes]:
        try:
            child_tpch = [x.tpch for x in self.children]
            child_tpch.sort()
            return crypto.blake2b(msgpack.packb([self.path.name, self.ctime_ns, child_tpch]))
        except TypeError:
            return None

    def update(self):
        for child in self.children:
            child.update()


def get_parent(path, max_depth=-1) -> FsParent:
    print('parent')
    hostname = platform.node()
    fsid = 'TODO'
    children = []
    next_child: FsEntry
    for entry in os.scandir(path):
        print(entry)
        if entry.is_dir(follow_symlinks=False):
            print(max_depth)
            if max_depth == 0:  # stop recursion
                next_child = FsParent(hostname=hostname, fsid=fsid, path=Path(entry))
            else:
                print(max_depth)
                next_child = get_parent(entry, max_depth=max_depth - 1)
        else:
            next_child = FsChild(path=Path(entry))
            next_child.update(b2=False)
        children.append(next_child)

    children.sort(key=lambda x: x.path.name)
    for child in children:
        print(child)

    return FsParent(hostname=hostname, fsid=fsid, path=Path(path), children=children, loaded=True)
