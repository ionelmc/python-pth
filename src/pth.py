from __future__ import print_function

import errno
import posixpath
import os
import shutil
import sys
import tempfile
import time
import zipfile
from functools import wraps
from os import path as ospath

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


class PTH(object):
    @property
    def cwd(self):
        return pth(os.getcwd())

    def __call__(self, *parts):
        path = ospath.join(*parts) if parts else ospath.curdir
        if zipfile.is_zipfile(path):
            return ZipPath(Path(path), zipfile.ZipFile(path))
        else:
            return Path(path)

pth = PTH()

identity = lambda x: x
method = lambda func: lambda self, *args, **kwargs: pth(func(self, *args, **kwargs))
attribute = lambda func: property(lambda self: pth(func(self)))
raw_attribute = property
nth_attribute = lambda func, position: property(lambda path: func(path)[position])


@property
def unavailable(_):
    raise NotImplementedError("Not available here.")


def expect_directory(func):
    @wraps(func)
    def expect_directory_wrapper(self, *args):
        if not self.isdir:
            raise PathMustBeDirectory("%r is not a directory nor a zip !" % self)
        else:
            return func(self, *args)
    return expect_directory_wrapper


def pair_attribute(func, first_func=identity, second_func=identity):
    def pair_attribute_wrapper(self):
        first_value, second_value = func(self)
        return first_func(first_value), second_func(second_value)
    return property(pair_attribute_wrapper)

string = str  # flake8: noqa


class AbstractPath(string):
    name = basename = attribute(ospath.basename)
    dir = dirname = attribute(ospath.dirname)
    isabs = raw_attribute(ospath.isabs)
    pathsplit = splitpath = pair_attribute(ospath.split, pth, pth)
    drive = nth_attribute(ospath.splitdrive, 0)
    ext = nth_attribute(ospath.splitext, 1)

    def __repr__(self):
        return 'pth.Path(%r)' % string(self)

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
    def parts(self):
        return [pth(part or ospath.sep) for part in self.split(ospath.sep)]


class Path(AbstractPath):
    abs = abspath = attribute(ospath.abspath)
    exists = raw_attribute(ospath.exists)
    lexists = raw_attribute(ospath.lexists)
    expanduser = attribute(ospath.expanduser)
    expandvars = attribute(ospath.expandvars)
    atime = raw_attribute(ospath.getatime)
    ctime = raw_attribute(ospath.getctime)
    mtime = raw_attribute(ospath.getmtime)
    size = raw_attribute(ospath.getsize)
    isdir = raw_attribute(ospath.isdir)
    isfile = raw_attribute(ospath.isfile)
    islink = raw_attribute(ospath.islink)
    ismount = raw_attribute(ospath.ismount)
    joinpath = __div__ = __floordiv__ = __truediv__ = method(ospath.join)
    normcase = attribute(ospath.normcase)
    normpath = attribute(ospath.normpath)
    norm = attribute(lambda self: ospath.normcase(ospath.normpath(self)))
    real = realpath = attribute(ospath.realpath)
    rel = relpath = method(ospath.relpath)
    same = samefile = method(ospath.samefile)
    drivesplit = splitdrive = pair_attribute(ospath.splitdrive, identity, pth)
    extsplit = splitext = pair_attribute(ospath.splitext, pth, identity)

    @property
    def tree(self):
        for path in self.list:
            yield path
            if path.isdir:
                for i in path.tree:
                    yield i

    @property
    @expect_directory
    def list(self):
        for name in os.listdir(self):
            yield pth(ospath.join(self, name))

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

    @property
    def cd(self):
        return WorkingDir(self)

    def copy(self, dest):
        if not isinstance(dest, Path):
            dest = Path(dest)
        if dest.isdir:
            dest = dest / self.name
        shutil.copyfile(self, dest)
        return dest


class WorkingDirAlreadyActive(Exception):
    pass


class WorkingDir(Path):
    previous = None
    __in_context = False

    @expect_directory
    def __cd(self):
        self.previous = Path(os.getcwd())
        os.chdir(self)
        return self

    def __enter__(self):
        if self.__in_context:
            raise WorkingDirAlreadyActive("Already switched to %r" % self)
        self.__in_context = True
        return self.__cd()

    def __call__(self):
        if self.__in_context:
            raise WorkingDirAlreadyActive("Already switched to %r" % self)
        return self.__cd()

    def __exit__(self, *exc):
        os.chdir(self.previous)

    def __repr__(self):
        return 'pth.WorkingDir(%r)' % string(self)


zippath_attribute = lambda func: property(lambda self: ZipPath(
    func(self._ZipPath__zippath),
    self._ZipPath__zipobj,
    self._ZipPath__relpath,
))


class ZipPath(Path):
    abs = abspath = zippath_attribute(ospath.abspath)

    @property
    def exists(self):
        if not ospath.exists(self.__zippath):
            return False
        path = self.__relpath.rstrip(ospath.sep)
        if not path:
            return True
        try:
            self.__zipinfo(posixpath.normpath(path))
        except KeyError:
            try:
                self.__zipinfo(posixpath.normpath(path))
            except KeyError:
                return False
        return True

    expanduser = zippath_attribute(ospath.expanduser)
    expandvars = property(lambda self: ZipPath(
        ospath.expandvars(self.__zippath),
        self.__zipobj,
        ospath.expandvars(self.__relpath),
    ))

    @property
    def atime(self):
        path = self.__relpath.rstrip(ospath.sep)
        if not path:
            return self.__zippath.atime
        else:
            raise NotImplementedError("Not supported for files inside the zip.")

    @property
    def ctime(self):
        path = self.__relpath.rstrip(ospath.sep)
        if not path:
            return self.__zippath.ctime
        try:
            zi = self.__zipinfo(posixpath.normpath(path))
        except KeyError as exc:
            raise_(PathDoesNotExist, exc)
        else:
            return time.mktime(zi.date_time + (-1, -1, 0))

    @property
    def mtime(self):
        path = self.__relpath.rstrip(ospath.sep)
        if not path:
            return self.__zippath.mtime
        else:
            raise NotImplementedError("Not supported for files inside the zip.")

    @property
    def size(self):
        path = self.__relpath.rstrip(ospath.sep)
        if not path:
            return self.__zippath.size
        try:
            zi = self.__zipinfo(posixpath.normpath(path))
        except KeyError as exc:
            raise_(PathDoesNotExist, exc)
        else:
            return zi.file_size

    @property
    def isdir(self):
        path = self.__relpath.rstrip(ospath.sep)
        if not path:
            return True
        try:
            self.__zipinfo(posixpath.normpath(path) + '/')
        except KeyError:
            return False
        else:
            return True

    @property
    def isfile(self):
        path = self.__relpath.rstrip(ospath.sep)
        if not path:
            return False
        try:
            self.__zipinfo(posixpath.normpath(path))
        except KeyError:
            return False
        else:
            return True

    islink = raw_attribute(ospath.islink)
    ismount = raw_attribute(ospath.ismount)

    def joinpath(self, *paths):
        for i in reversed(paths):
            if isinstance(i, Path) and i.isabs:
                return i
        return ZipPath(self.__zippath, self.__zipobj, ospath.join(self.__relpath, *paths))

    __div__ = __floordiv__ = __truediv__ = joinpath
    lexists = unavailable
    normcase = zippath_attribute(ospath.normcase)
    normpath = zippath_attribute(ospath.normpath)
    norm = zippath_attribute(lambda self: ospath.normcase(ospath.normpath(self)))
    real = realpath = zippath_attribute(ospath.realpath)

    def relpath(self, other):
        if isinstance(other, ZipPath) and other.__zippath == self.__zippath:
            return ZipPath(
                "",
                self.__zipobj,
                ospath.relpath(
                    ospath.join(self.__zippath, self.__relpath),
                    ospath.join(self.__zippath, other.__relpath),
                )
            )
        else:
            return pth(ospath.relpath(self, other))
    rel = relpath

    drivesplit = splitdrive = pair_attribute(ospath.splitdrive, identity, lambda path: ZipPath.from_string(path))
    extsplit = splitext = pair_attribute(ospath.splitext, lambda path: ZipPath.from_string(path), identity)

    def __new__(cls, path, zipobj=None, relpath=""):
        if not zipfile.is_zipfile(path):
            return pth(ospath.join(path, relpath).rstrip(ospath.sep))
        obj = string.__new__(cls, ospath.join(path, relpath).rstrip(ospath.sep))
        obj.__zippath = path
        obj.__zipobj = zipfile.ZipFile(path) if zipobj is None else zipobj
        obj.__relpath = relpath
        obj.__zipinfo = obj.__zipobj.getinfo
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
                return ZipPath(lead.__zippath, lead.__zipobj, ospath.join(*tails))
            else:
                return path
        else:
            return lead

    def __repr__(self):
        return 'pth.ZipPath(%r, None, %r)' % (str(self.__zippath), str(self.__relpath))

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
pth.ZipPath = pth.zip = ZipPath
pth.TempPath = pth.tmp = TempPath
pth.WorkingDir = pth.wd = WorkingDir
pth.WorkingDirAlreadyActive = WorkingDirAlreadyActive
pth.PathError = PathError
pth.PathMustBeFile = PathMustBeFile
pth.PathMustBeDirectory = PathMustBeDirectory
pth.PathDoesNotExist = PathDoesNotExist
pth.__name__ = __name__
pth.__file__ = __file__
pth.__package__ = __package__
pth.__version__ = "0.3.0"
pth.__mod = sys.modules['pth']  # gotta do this, otherwise it gets garbage collected
sys.modules['pth'] = pth
