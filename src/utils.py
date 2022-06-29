import builtins
import inspect
import sys


def dprint(*args, **kwargs):
    caller = inspect.stack()[1]
    builtins.print(f'\r<{caller.function}:{caller.lineno}>', *args, '\033[K', **kwargs, file=sys.stderr)
