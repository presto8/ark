import base64
import msgpack
import os
from dataclasses import dataclass
from pathlib import Path
from src import crypto


def b64e(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.b64encode(data, altchars=b"+-").decode()


def b64d(data):
    return base64.b64decode(data, altchars=b"+-")


@dataclass
class Store:
    path: Path

    def __post_init__(self):
        os.makedirs(self.path, exist_ok=True)

    def put(self, selector, data: bytes = b"") -> str:
        name = "_".join(self.wrap_selector(selector))
        return self.putb(name, data)

    def getb(self, name: str) -> bytes:
        return open(self.path / name, "rb").read()

    def putb(self, name: str, data: bytes):
        with open(self.path / name, "wb") as f:
            f.write(data)
        return name

    def have(self, selector) -> bool:
        name = "_".join(self.wrap_selector(selector))
        return (self.path / name).exists()

    def match(self, selector, num_to_match=None):
        n = num_to_match or len(selector)
        want = self.wrap_selector(selector)
        matches = []
        for entry in os.scandir(self.path):
            have = entry.name.split("_")
            if have[:n] == want[:n]:
                matches.append((have[:n], have[n:]))
        return matches

    @staticmethod
    def wrap_selector(selector):
        encrypted = [crypto.blake2b(msgpack.packb(x))[:32] for x in selector]
        return [b64e(x) for x in encrypted]

    # guid: str
    # label: Optional[str] = None
    # cache
    # remotes
    # objects
