#!/usr/bin/env python

import argparse
import sys

HELP = """
Ark by Preston Hunt <me@prestonhunt.com>
https://github.com/presto8/ark

An experimental chunk-based backup program. This is a proof-of-concept
implementation to explore concepts which may not be addressed fully in
currently available backup programs.
"""


def parse_args():
    parser = argparse.ArgumentParser(description=HELP, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--verbose', default=False, action='store_true', help='show more detailed messages')
    parser.add_argument('--debug', action='store_true')

    subparsers = parser.add_subparsers(dest='command')

    # 'ark backup'
    x = subparsers.add_parser('backup', help='backup pathspec (recursively descend dirs)')
    x.add_argument('pathspec', nargs='+', default=('.',), help="paths to process")
    x.add_argument('--dry-run', '-n', action='store_true', help='do not backup, preview what would happen only')

    args, unknown_args = parser.parse_known_args()
    args.unknown_args = unknown_args

    if args.command is None:
        parser.print_help()
        raise SystemExit(0)

    return args


def main():
    args = parse_args()
    if args.command:
        print("TODO command:", args)
    else:
        print(args)


class Fail(Exception):
    pass


def entrypoint():
    try:
        main()
    except Fail as f:
        print(*f.args, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Ctrl+C")
