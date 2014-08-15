import pth
import sys

if sys.version_info[0] == 2:
    pth.PathError.__name__ = 'pth.' + pth.PathError.__name__
    pth.PathMustBeFile.__name__ = 'pth.' + pth.PathMustBeFile.__name__
    pth.PathMustBeDirectory.__name__ = 'pth.' + pth.PathMustBeDirectory.__name__
    pth.PathDoesNotExist.__name__ = 'pth.' + pth.PathDoesNotExist.__name__
