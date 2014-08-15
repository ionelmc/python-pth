from __future__ import print_function

import errno
import os
import shutil
import sys
import tempfile
import time
import zipfile

PY2 = sys.version_info[0] == 2


if PY2:
    def exec_(_code_, _globs_=None, _locs_=None):
        """Execute code in a namespace."""
        if _globs_ is None:
            frame = sys._getframe(1)
            _globs_ = frame.f_globals
            if _locs_ is None:
                _locs_ = frame.f_locals
            del frame
        elif _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")

    exec_("""def raise_(tp, value):
    raise tp, value, sys.exc_info()[2]
""")
else:
    def raise_(tp, value):
        raise tp(value)


class PathError(Exception):
    pass


class PathMustBeDirectory(PathError):
    pass


class PathMustBeFile(PathError):
    pass


class PathDoesNotExist(PathError):
    pass


def pth(path='.'):
    if zipfile.is_zipfile(path):
        return ZipPath(Path(path), zipfile.ZipFile(path))
    else:
        return Path(path)

identity = lambda x: x
method = lambda func: lambda self, *args, **kwargs: pth(func(self, *args, **kwargs))
attribute = lambda func: property(lambda self: pth(func(self)))
raw_attribute = property
nth_attribute = lambda func, position: property(lambda path: func(path)[position])


@property
def unavailable(self):
    raise AttributeError("Not available here.")


def pair_attribute(func, first_func=identity, second_func=identity):
    def pair_attribute_wrapper(self):
        first_value, second_value = func(self)
        return first_func(first_value), second_func(second_value)
    return property(pair_attribute_wrapper)

string = os.path.supports_unicode_filenames and unicode or str  # flake8: noqa


class Path(string):
    abs = abspath = attribute(os.path.abspath)
    name = basename = attribute(os.path.basename)
    dir = dirname = attribute(os.path.dirname)
    exists = raw_attribute(os.path.exists)
    expanduser = attribute(os.path.expanduser)
    expandvars = attribute(os.path.expandvars)
    atime = raw_attribute(os.path.getatime)
    ctime = raw_attribute(os.path.getctime)
    mtime = raw_attribute(os.path.getmtime)
    size = raw_attribute(os.path.getsize)
    isabs = raw_attribute(os.path.isabs)
    isdir = raw_attribute(os.path.isdir)
    isfile = raw_attribute(os.path.isfile)
    islink = raw_attribute(os.path.islink)
    ismount = raw_attribute(os.path.ismount)
    joinpath = __div__ = __floordiv__ = __truediv__ = method(os.path.join)
    lexists = raw_attribute(os.path.lexists)
    normcase = attribute(os.path.normcase)
    normpath = attribute(os.path.normpath)
    realpath = attribute(os.path.realpath)
    relpath = method(os.path.relpath)
    splitpath = pair_attribute(os.path.split, pth, pth)
    splitdrive = pair_attribute(os.path.splitdrive, identity, pth)
    splitext = pair_attribute(os.path.splitext, pth, identity)
    drive = nth_attribute(os.path.splitdrive, 0)
    ext = nth_attribute(os.path.splitext, 1)

    def __repr__(self):
        return '<Path %s>' % super(Path, self).__repr__()

    @property
    def tree(self):
        for path in self.list:
            yield path
            if path.isdir:
                for i in path.tree:
                    yield i

    @property
    def files(self):
        for path in self.list:
            if path.isfile:
                yield path

    @property
    def dirs(self):
        for path in self.list:
            if path.isdir:
                yield path

    @property
    def list(self):
        if not self.isdir:
            raise PathMustBeDirectory("%r is not a directory nor a zip !" % self)

        for name in os.listdir(self):
            yield pth(os.path.join(self, name))

    def __call__(self, *open_args, **open_kwargs):
        if not self.isdir:
            try:
                return open(self, *open_args, **open_kwargs)
            except IOError as exc:
                if exc.errno == errno.ENOENT:
                    raise_(PathMustBeFile, exc)
                else:
                    raise
        else:
            raise PathMustBeFile("%r is not a file !" % self)

zippath_attribute = lambda func: property(lambda self: ZipPath(
    func(self._ZipPath__zippath),
    self._ZipPath__zipobj,
    self._ZipPath__relpath,
))


class ZipPath(Path):
    abs = abspath = zippath_attribute(os.path.abspath)
    name = basename = attribute(os.path.basename)
    dir = dirname = attribute(os.path.dirname)

    @property
    def exists(self):
        path = self.__relpath.rstrip('/')
        if not path:
            return True
        try:
            self.__zipobj.getinfo(path)
        except KeyError:
            try:
                self.__zipobj.getinfo(path)
            except KeyError:
                return False
        return True

    expanduser = zippath_attribute(os.path.expanduser)
    expandvars = property(lambda self: ZipPath(
        os.path.expandvars(self.__zippath),
        self.__zipobj,
        os.path.expandvars(self.__relpath),
    ))
    atime = unavailable

    @property
    def ctime(self):
        path = self.__relpath.rstrip('/')
        if not path:
            return self.__zippath.ctime
        try:
            zi = self.__zipobj.getinfo(path)
        except KeyError as exc:
            raise_(PathDoesNotExist, exc)
        else:
            return time.mktime(zi.date_time + (-1, -1, 0))
    mtime = unavailable

    @property
    def size(self):
        path = self.__relpath.rstrip('/')
        if not path:
            return self.__zippath.size
        try:
            zi = self.__zipobj.getinfo(path)
        except KeyError as exc:
            raise_(PathDoesNotExist, exc)
        else:
            return zi.file_size

    isabs = raw_attribute(os.path.isabs)

    @property
    def isdir(self):
        path = self.__relpath.rstrip('/')
        if not path:
            return True
        try:
            self.__zipobj.getinfo(path + '/')
        except KeyError:
            return False
        else:
            return True

    @property
    def isfile(self):
        path = self.__relpath.rstrip('/')
        if not path:
            return False
        try:
            self.__zipobj.getinfo(path)
        except KeyError:
            return False
        else:
            return True

    islink = raw_attribute(os.path.islink)
    ismount = raw_attribute(os.path.ismount)

    def joinpath(self, *paths):
        for i in reversed(paths):
            if isinstance(i, Path) and i.isabs:
                return i
        return ZipPath(self.__zippath, self.__zipobj, os.path.join(self.__relpath, *paths))

    __div__ = __floordiv__ = __truediv__ = joinpath
    lexists = unavailable
    normcase = zippath_attribute(os.path.normcase)
    normpath = zippath_attribute(os.path.normpath)
    realpath = zippath_attribute(os.path.realpath)
    relpath = unavailable
    splitpath = pair_attribute(os.path.split, pth, pth)
    splitdrive = pair_attribute(os.path.splitdrive, identity, lambda path: ZipPath.from_string(path))
    splitext = pair_attribute(os.path.splitext, lambda path: ZipPath.from_string(path), identity)
    drive = nth_attribute(os.path.splitdrive, 0)
    ext = nth_attribute(os.path.splitext, 1)

    def __new__(cls, path, zipobj, relpath=""):
        if not zipfile.is_zipfile(path):
            return pth(os.path.join(path, relpath).rstrip('/'))
        obj = string.__new__(cls, os.path.join(path, relpath).rstrip('/'))
        obj.__zippath = path
        obj.__zipobj = zipobj
        obj.__relpath = relpath
        return obj

    @classmethod
    def from_string(cls, string):
        path = pth(string)
        if isinstance(path, ZipPath):
            return path
        lead, tails = path, []
        while lead and not lead.exists:
            lead, tail = lead.splitpath
            tails.append(tail)
        tails.reverse()
        if tails:
            if isinstance(lead, ZipPath):
                return ZipPath(lead.__zippath, lead.__zipobj, os.path.join(*tails))
            else:
                return path
        else:
            return lead

    def __repr__(self):
        return '<ZipPath %r / %r>' % (str(self.__zippath), str(self.__relpath))

    @property
    def tree(self):
        if not self.isdir:
            raise PathMustBeDirectory("%r is not a directory !" % self)

        for name in self.__zipobj.namelist():
            if name.startswith(self.__relpath):
                yield ZipPath(self.__zippath, self.__zipobj, name)

    @property
    def list(self):
        if not self.isdir:
            raise PathMustBeDirectory("%r is not a directory !" % self)

        for name in self.__zipobj.namelist():
            if name.startswith(self.__relpath):
                if '/' not in name[len(self.__relpath):].strip('/'):
                    yield ZipPath(self.__zippath, self.__zipobj, name)

    def __call__(self, *open_args, **open_kwargs):
        if self.isfile:
            return self.__zipobj.open(self.__relpath, *open_args, **open_kwargs)
        else:
            raise PathMustBeFile("%r is not a file !" % self)


class TempPath(Path):
    def __new__(cls, **mkdtemp_kwargs):
        return string.__new__(cls, tempfile.mkdtemp(**mkdtemp_kwargs))

    def __enter__(self):
        return self

    def __exit__(self, tt=None, tv=None, tb=None):
        shutil.rmtree(str(self))

    def __repr__(self):
        return '<TempPath %s>' % super(Path, self).__repr__()


pth.Path = Path
pth.ZipPath = ZipPath
pth.TempPath = TempPath
pth.PathError = PathError
pth.PathMustBeFile = PathMustBeFile
pth.PathMustBeDirectory = PathMustBeDirectory
pth.PathDoesNotExist = PathDoesNotExist
pth.__name__ = __name__
pth.__file__ = __file__
pth.__package__ = __package__
pth.__mod = sys.modules['pth']  # gotta do this, otherwise it gets garbage collected
sys.modules['pth'] = pth
