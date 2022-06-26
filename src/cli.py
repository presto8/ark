#!/usr/bin/env python

import argparse
import inspect
import sys
from pathlib import Path
from . import ark

HELP = """
Ark by Preston Hunt <me@prestonhunt.com>
https://github.com/presto8/ark

An experimental chunk-based backup program. This is a proof-of-concept
implementation to explore concepts which may not be addressed fully in
currently available backup programs.
"""


def parse_args(argv):
    parser = argparse.ArgumentParser(description=HELP, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--verbose', default=False, action='store_true', help='show more detailed messages')
    parser.add_argument('--debug', action='store_true')

    subparsers = parser.add_subparsers(dest='command')

    # 'ark backup'
    x = subparsers.add_parser('backup', help='backup pathspec (recursively descend dirs)')
    x.add_argument('pathspec', nargs='+', default=('.',), help="paths to process")
    x.add_argument('--dry-run', '-n', action='store_true', help='do not backup, preview what would happen only')

    args, unknown_args = parser.parse_known_args(argv)
    args.unknown_args = unknown_args

    if args.command is None:
        parser.print_help()
        raise SystemExit(1)

    return args


def cli_mapper(args):
    func = getattr(ark, args.command.replace("-", "_"))
    sig = inspect.signature(func)
    func_args = sig.parameters.keys()
    missing_args = [arg for arg in func_args if arg not in arg]
    if missing_args:
        raise Fail(f"missing arguments for {func}: {missing_args}")  # pragma: no cover
    pass_args = {k: v for k, v in args.__dict__.items() if k in func_args}
    if 'pathspec' in pass_args.keys():
        pass_args['pathspec'] = [Path(path) for path in pass_args['pathspec']]
    return func(**pass_args)


def main(argv):
    args = parse_args(argv)
    cli_mapper(args)


class Fail(Exception):
    pass


def entrypoint():  # pragma: no cover
    try:
        main(sys.argv[1:])
    except Fail as f:
        print(*f.args, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Ctrl+C")
