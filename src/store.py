import base64
import os
from dataclasses import dataclass
from pathlib import Path
from src import fs


def b64e(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.b64encode(data, altchars=b"+-").decode()


def b64d(data):
    return base64.b64decode(data, altchars=b"+-").decode()


def parse_object(obj) -> tuple[str, bytes]:
    if isinstance(obj, fs.FsChild):
        return f"{b64e(obj.pth)}_{b64e(obj.ptch)}", b""
    elif isinstance(obj, str):
        return obj, b""
    else:
        raise


@dataclass
class Store:
    path: Path

    def __post_init__(self):
        print(type(self.path))
        os.makedirs(self.path)

    def put(self, obj) -> str:
        "Returns name of path on store"
        if isinstance(obj, fs.FsChild):
            name = f"{b64e(obj.pth)}_{b64e(obj.ptch)}"
            data = b""
        else:
            raise
        self.putb(name, data)
        return name

    def getb(self, name: str) -> bytes:
        return open(self.path / name, "rb").read()
        return open(self.path / b64e(name), "rb").read()

    def putb(self, name: str, data: bytes):
        with open(self.path / name, "wb") as f:
            f.write(data)

    def have(self, obj) -> bool:
        name, _ = parse_object(obj)
        return (self.path / name).exists()

    # guid: str
    # label: Optional[str] = None
    # cache
    # remotes
    # objects
