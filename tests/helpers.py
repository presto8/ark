import os

from pathlib import Path
from types import SimpleNamespace

from src import crypto


def phf1(data):
    pk = b"38DB2C2847539F57AB46D3D09A3EC46F571E3B9F"
    return crypto.phf1(pk, data)


def create_file(path: Path, contents: str = ""):
    "Returns SimpleNamespace(path, contents, size, sha256)"
    if not os.path.exists(path.parent):
        path.parent.mkdir()
    path.write_text(contents)
    return SimpleNamespace(path=path, contents=contents, size=len(contents))
