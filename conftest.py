import os


def _silly(*args, **kwargs):
    raise NotImplementedError((args, kwargs))


def _fill(mod, name):
    if not hasattr(mod, name):
        setattr(mod, name, _silly)

_fill(os, 'lchmod')
_fill(os, 'lchown')
_fill(os, 'chflags')
_fill(os, 'lchflags')

import pth
import sys

if sys.version_info[0] == 2:
    pth.PathError.__name__ = 'pth.' + pth.PathError.__name__
    pth.PathMustBeFile.__name__ = 'pth.' + pth.PathMustBeFile.__name__
    pth.PathMustBeDirectory.__name__ = 'pth.' + pth.PathMustBeDirectory.__name__
    pth.PathDoesNotExist.__name__ = 'pth.' + pth.PathDoesNotExist.__name__


