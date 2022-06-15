#!/usr/bin/env python

import os
import struct
from pathlib import Path


# References:
# - https://gist.github.com/jbeda/5c79d2b1434f0018d693
# - nixos.org/~eelco/pubs/phd-thesis.pdf


def serialize(fso):
    return serialise(fso)


def serialise(fso):
    return str_("nix-archive-1") + serialise1(fso)


def serialise1(fso):
    return str_("(") + serialise2(Path(fso)) + str_(")")


def serialise2(fso: Path):
    if fso.is_symlink():
        return str_("type") + str_("symlink") + str_("target") + str_(os.readlink(fso))
    elif fso.is_file():
        executable = (str_("executable") + str_("")) if os.access(fso, os.X_OK) else b""
        return str_("type") + str_("regular") + executable + str_("contents") + str_(open(fso).read())
    elif fso.is_dir():
        return str_("type") + str_("directory") + b"".join([serialiseEntry(fso, x) for x in sortEntries(fso)])
    else:
        raise Exception(fso)


def serialiseEntry(fso, entry):
    return str_("entry") + str_("(") + str_("name") + str_(str(entry.relative_to(fso))) + str_("node") + serialise1(entry) + str_(")")


def str_(s):
    if type(s) is str:
        s = s.encode('utf-8')
    return int_(len(s)) + pad(s)


def int_(n):
    # = the 64-bit little endian representation of the number n
    return struct.pack("<Q", n)


def pad(s):
    # the byte sequence s, padded with 0s to a multiple of 8 bytes
    padding = (8 - len(s) % 8) % 8
    return s + (b'\x00' * padding)


def scantree(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield Path(entry)


def sortEntries(path):
    s = sorted(scantree(path), key=lambda x: str(x))
    print(s)
    return s
