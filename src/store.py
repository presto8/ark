import msgpack
import os
from dataclasses import dataclass
from src import crypto
from collections import Counter


@dataclass
class Store:
    path: os.PathLike

    def __post_init__(self):
        os.makedirs(self.path, exist_ok=True)

    def put(self, obj) -> str:
        "Put an object that implements the selector method."
        name = "_".join(self.wrap_selector(obj.selector))
        return self.putb(name, obj.read())

    def getb(self, name: str) -> bytes:
        return open(os.path.join(self.path, name), "rb").read()

    def putb(self, name: str, data: bytes):
        with open(os.path.join(self.path, name), "wb") as f:
            f.write(data)
        return name

    def have(self, obj) -> bool:
        name = "_".join(self.wrap_selector(obj.selector))
        return os.path.exists(os.path.join(self.path, name))

    def match(self, query_selector):
        "Returns objects matching any selector."
        want = self.wrap_selector(query_selector)
        matches = Counter()
        for entry in os.scandir(self.path):
            have = entry.name.split("_")
            for w in want:
                if w in have:
                    matches[w] += 1
        return [matches[w] for w in want]

    @staticmethod
    def wrap_selector(selector):
        encrypted = [crypto.blake2b(msgpack.packb(x))[:32] for x in selector]
        return [crypto.b64e(x) for x in encrypted]

    # guid: str
    # label: Optional[str] = None
    # cache
    # remotes
    # objects
