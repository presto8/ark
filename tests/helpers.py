#!/usr/bin/env python

from pathlib import Path
from types import SimpleNamespace
import hashlib
import os


def create_file(path: Path, contents: str = ""):
    "Returns SimpleNamespace(path, contents, size, sha256)"
    if not os.path.exists(path.parent):
        path.parent.mkdir()
    path.write_text(contents)
    return SimpleNamespace(path=path, contents=contents, size=len(contents),
                           sha256=hashlib.sha256(contents.encode()).hexdigest())
