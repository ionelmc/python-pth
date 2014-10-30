from __future__ import print_function

import errno
import os
import posixpath
import shutil
import sys
import tempfile
import time
import zipfile
from os import path as ospath


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
DECENT_PY3 = sys.version_info[:2] >= (3, 3)


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


@property
def unavailable(_):
    raise NotImplementedError("Not available here.")

string = str  # flake8: noqa


class AbstractPath(string):
    name = basename = property(lambda self: pth(ospath.basename(self)))
    dir = dirname = property(lambda self: pth(ospath.dirname(self)))
    isabs = property(lambda self: ospath.isabs(self))

    @property
    def splitpath(self):
        first, second = ospath.split(self)
        return pth(first), pth(second)
    pathsplit = splitpath
    drive = property(lambda self: ospath.splitdrive(self)[0])
    ext = property(lambda self: ospath.splitext(self)[1])
    stem = property(lambda self: ospath.splitext(ospath.basename(self))[0])

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
    abs = abspath = property(lambda self: pth(ospath.abspath(self)))
    exists = property(lambda self: ospath.exists(self))
    lexists = property(lambda self: ospath.lexists(self))
    expanduser = property(lambda self: pth(ospath.expanduser(self)))
    expandvars = property(lambda self: pth(ospath.expandvars(self)))
    atime = property(lambda self: ospath.getatime(self))
    ctime = property(lambda self: ospath.getctime(self))
    mtime = property(lambda self: ospath.getmtime(self))
    size = property(lambda self: ospath.getsize(self))
    isdir = property(lambda self: ospath.isdir(self))
    isfile = property(lambda self: ospath.isfile(self))
    islink = property(lambda self: ospath.islink(self))
    ismount = property(lambda self: ospath.ismount(self))
    joinpath = __div__ = __floordiv__ = __truediv__ = lambda self, *args: pth(ospath.join(self, *args))
    normcase = property(lambda self: pth(ospath.normcase(self)))
    normpath = property(lambda self: pth(ospath.normpath(self)))
    norm = property(lambda self: pth(ospath.normcase(ospath.normpath(self))))
    real = realpath = property(lambda self: pth(ospath.realpath(self)))
    rel = relpath = lambda self, start: pth(ospath.relpath(self, start))
    same = samefile = lambda self, other: ospath.samefile(self, other)
    #isaccessible = access = lambda self, mode: os.access(self, mode)
    #isexecutable
    #isreadable
    #iswritable

    @property
    def splitdrive(self):
        first, second = ospath.splitdrive(self)
        return first, pth(second)
    drivesplit = splitdrive

    @property
    def splitext(self):
        first, second = ospath.splitext(self)
        return pth(first), second
    extsplit = splitext

    def chmod(self, mode, follow_symlinks=True):
        if follow_symlinks:
            return os.chmod(self, mode)
        else:
            if DECENT_PY3:
                os.chmod(self, mode, follow_symlinks=follow_symlinks)
            else:
                os.lchmod(self, mode)

    def chown(self, uid, gid, follow_symlinks=True):
        if follow_symlinks:
            os.chown(self, uid, gid)
        else:
            if DECENT_PY3:
                os.chown(self, uid, gid, follow_symlinks=follow_symlinks)
            else:
                os.lchown(self, uid, gid)

    lchmod = lambda self, mode: self.chmod(mode, follow_symlinks=False)
    lchown = lambda self, uid, gid: self.chown(uid, gid, follow_symlinks=False)

    @property
    def tree(self):
        for path in self.list:
            yield path
            if path.isdir:
                for i in path.tree:
                    yield i

    @property
    def list(self):
        if not self.isdir:
            raise PathMustBeDirectory("%r is not a directory nor a zip !" % self)

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

    def __cd(self):
        if not self.isdir:
            raise PathMustBeDirectory("%r is not a directory!" % self)

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

    islink = property(lambda self: ospath.islink(self))
    ismount = property(lambda self: ospath.ismount(self))

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

    @property
    def splitdrive(self):
        first, second = ospath.splitdrive(self)
        return first, ZipPath.from_string(second)
    drivesplit = splitdrive

    @property
    def splitext(self):
        first, second = ospath.splitext(self)
        return ZipPath.from_string(first), second
    extsplit = splitext

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
            raise PathMustBeDirectory("%r is not a directory!" % self)

        for name in self.__zipobj.namelist():
            if name.startswith(self.__relpath):
                yield ZipPath(self.__zippath, self.__zipobj, name)

    @property
    def list(self):
        if not self.isdir:
            raise PathMustBeDirectory("%r is not a directory!" % self)

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
