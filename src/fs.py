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
class FsChild:
    path: Path
    ctime_ns: Optional[int] = None  # None for a parent
    b2: Optional[bytes] = None      # None for a parent

    @property
    def is_parent(self):
        return self.b2 is None and self.ctime_ns is None

    def update(self, ctime_ns=True, b2=True):
        if self.is_parent:
            return
        if ctime_ns:
            self.ctime_ns = self.path.stat(follow_symlinks=False).st_ctime_ns
        if b2:
            if self.path.is_symlink():
                contents = os.readlink(self.path.path).encode()
            else:
                contents = open(self.path, "rb").read()
            self.b2 = crypto.blake2b(contents)

    @property
    def _msgpack(self):
        payload = [self.path.name, self.ctime_ns, self.b2]
        return msgpack.packb([self.path.name, self.ctime_ns, self.b2])

    @property
    def tpch(self):
        if not self.ctime_ns or not self.b2:
            return None
        return crypto.blake2b(self._msgpack)


@dataclass
class FsParent:
    hostname: str
    fsid: str
    path: Path
    children: list[FsChild] = field(default_factory=list)

    @property
    def ctime_ns(self) -> Optional[int]:
        try:
            return max([x.ctime_ns for x in self.children])
        except TypeError:
            return None

    @property
    def tpch(self) -> Optional[bytes]:
        try:
            payload = b"".join(x.tpch for x in self.children)
            return crypto.blake2b(payload)
        except TypeError:
            return None

    def update(self):
        for child in self.children:
            child.update()


def get_parent(path) -> FsParent:
    base = dict(hostname=platform.node(), fsid='TODO', path=Path(path))
    children = []
    for entry in os.scandir(path):
        next_child = dict(path=entry)
        if not entry.is_dir(follow_symlinks=False):
            next_child['ctime_ns'] = entry.stat(follow_symlinks=False).st_ctime_ns
        children.append(FsChild(**next_child))

    return FsParent(**base, children=sorted(children, key=lambda x: x.path.name))
