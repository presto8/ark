import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Store:
    path: Path

    def get(self, name):
        return open(self.path / name, "rb").read()

    def put(self, name, value):
        with open(self.path / name, "wb") as f:
            f.write(value)

    def have(self, name):
        return os.path.exists(self.path / name)

    # guid: str
    # label: Optional[str] = None
    # cache
    # remotes
    # objects
