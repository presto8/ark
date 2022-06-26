import os

from collections import Counter
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


def create_test_files(dir_path, structure):
    result = SimpleNamespace(num_files=0, newest_file_ctime_ns=0)
    for name, value in structure.items():
        if isinstance(value, str):
            newf = dir_path / name
            if value.startswith("link:"):
                # create a symlink
                os.symlink(value[5:], newf)
            else:
                # create a file
                create_file(newf, value)
            result.num_files += 1
            result.newest_file_ctime_ns = newf.stat().st_ctime_ns
        elif isinstance(value, dict):
            # directory - recurse
            sub_result = create_test_files(dir_path / name, value)
            result.num_files += sub_result.num_files
            result.newest_file_ctime_ns = max(result.newest_file_ctime_ns, sub_result.newest_file_ctime_ns)
        else:
            # error
            raise  # pragma: no cover
    return result
