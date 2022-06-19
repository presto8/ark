#!/usr/bin/env python

import argparse
import os
import subprocess
import sys
from typing import NamedTuple

HELP = """
Ark by Preston Hunt <me@prestonhunt.com>
https://github.com/presto8/ark

An experimental chunk-based backup program. This is a proof-of-concept
implementation to explore concepts which may not be addressed fully in
currently available backup programs.
"""


def parse_args():
    parser = argparse.ArgumentParser(description=HELP, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('paths', nargs='*', help='paths to process')
    parser.add_argument('--verbose', default=False, action='store_true', help='show more detailed messages')
    return parser.parse_args()


def main():
    if ARGS.verbose:
        print("verbose mode enabled, will display abspath")
    for path in ARGS.paths:
        print(worker(path))


def scantree(path, follow_symlinks=False, recursive=True):
    passthru = [follow_symlinks, recursive]
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=follow_symlinks) and recursive:
            yield from scantree(entry.path, *passthru)
        else:
            yield entry


class ParsedPath(NamedTuple):
    ok: bool
    input_path: str
    basename: str
    abspath: str


def parse_path(path) -> ParsedPath:
    result = dict(ok=False, input_path=path)
    result['basename'] = os.path.basename(path)
    result['abspath'] = os.path.abspath(path)
    result['ok'] = True
    return ParsedPath(**result)


def worker(path) -> str:
    ppath = parse_path(path)
    if ARGS.verbose:
        print(ppath)
    return ppath.abspath if ARGS.verbose else ppath.basename


def run(*args):
    return subprocess.run(args, capture_output=True, text=True)


class Fail(Exception):
    pass


def entrypoint():
    try:
        # Command-line arguments are considered as immutable constants of the
        # universe, and thus are globally available in this script.
        global ARGS
        ARGS = parse_args()
        main()
    except Fail as f:
        print(*f.args, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Ctrl+C")
