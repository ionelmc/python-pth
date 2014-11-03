from __future__ import print_function

import errno
import os
import posixpath
import shutil
import sys
import tempfile
import time
import zipfile
import io
from os import path as ospath


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY32 = sys.version_info[:2] >= (3, 2)
PY33 = sys.version_info[:2] >= (3, 3)

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
        if parts:
            path = ospath.join(*parts)
        else:
            path = ospath.curdir

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


class cached_property(object):
    """ A property that is only computed once per instance and then replaces
        itself with an ordinary attribute. Deleting the attribute resets the
        property.

        Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
        """

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class LazyObjectProxy(object):
    __lop_factory__ = None

    def __init__(self, factory):
        super(LazyObjectProxy, self).__setattr__('__lop_factory__', factory)

    @cached_property
    def __lop_subject__(self):
        return self.__lop_factory__()

    def __call__(self, *args, **kwargs):
        return self.__lop_factory__(*args, **kwargs)

    def __getitem__(self, arg):
        return self.__lop_subject__[arg]

    def __setitem__(self, arg, val):
        self.__lop_subject__[arg] = val

    def __delitem__(self, arg):
        del self.__lop_subject__[arg]

    def __getslice__(self, i, j):
        return self.__lop_subject__[i:j]

    def __setslice__(self, i, j, val):
        self.__lop_subject__[i:j] = val

    def __delslice__(self, i, j):
        del self.__lop_subject__[i:j]

    def __contains__(self, ob):
        return ob in self.__lop_subject__

    for name in 'setattr delattr getattr bool repr str hash len abs complex int long float iter cmp coerce divmod'.split():
        exec("def __%s__(self, *args): return %s(self.__lop_subject__, *args)" % (name, name))

    for name, op in [
        ('lt', '<'), ('gt', '>'), ('le', '<='), ('ge', '>='),
        ('eq', ' == '), ('ne', '!=')
    ]:
        exec("def __%s__(self, ob): return self.__lop_subject__ %s ob" % (name, op))

    for name, op in [('neg', '-'), ('pos', '+'), ('invert', '~')]:
        exec("def __%s__(self): return %s self.__lop_subject__" % (name, op))

    for name, op in [
        ('or', '|'),  ('and', '&'), ('xor', '^'), ('lshift', '<<'), ('rshift', '>>'),
        ('add', '+'), ('sub', '-'), ('mul', '*'), ('div', '/'), ('mod', '%'),
        ('truediv', '/'), ('floordiv', '//')
    ]:
        exec((
            "def __%(name)s__(self, ob):\n"
            "    return self.__lop_subject__ %(op)s ob\n"
            "\n"
            "def __r%(name)s__(self, ob):\n"
            "    return ob %(op)s self.__lop_subject__\n"
            "\n"
            "def __i%(name)s__(self, ob):\n"
            "    self.__lop_subject__ %(op)s=ob\n"
            "    return self\n"
        ) % locals())

    del name, op

    # Oddball signatures
    def __index__(self):
        return self.__lop_subject__.__index__()

    def __rdivmod__(self, ob):
        return divmod(ob, self.__lop_subject__)

    def __pow__(self, *args):
        return pow(self.__lop_subject__, *args)

    def __ipow__(self, ob):
        self.__lop_subject__ **= ob
        return self

    def __rpow__(self, ob):
        return pow(ob, self.__lop_subject__)


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
    joinpath = pathjoin = __div__ = __floordiv__ = __truediv__ = lambda self, *args: pth(ospath.join(self, *args))
    normcase = property(lambda self: pth(ospath.normcase(self)))
    normpath = property(lambda self: pth(ospath.normpath(self)))
    norm = property(lambda self: pth(ospath.normcase(ospath.normpath(self))))
    real = realpath = property(lambda self: pth(ospath.realpath(self)))
    rel = relpath = lambda self, start: pth(ospath.relpath(self, start))
    same = samefile = lambda self, other: ospath.samefile(self, other)
    if hasattr(os, 'link'):
        if PY33:
            link = lambda self, dest, follow_symlinks=True, **kwargs: os.link(self, dest, follow_symlinks=follow_symlinks, **kwargs)
        else:
            link = lambda self, dest: os.link(self, dest)
    if PY33:
        stat = property(lambda self: LazyObjectProxy(lambda **kwargs: os.stat(self, **kwargs)))
        lstat = property(lambda self: LazyObjectProxy(lambda **kwargs: os.lstat(self, **kwargs)))
    else:
        stat = property(lambda self: os.stat(self))
        lstat = property(lambda self: os.lstat(self))
    isreadable = property(lambda self: LazyObjectProxy(lambda **kwargs: os.access(self, os.R_OK, **kwargs)))
    mkdir = lambda self: os.mkdir(self)
    makedirs = lambda self: os.makedirs(self)
    if hasattr(os, 'pathconf'):
        pathconf = lambda self, name: os.pathconf(self, name)
    if hasattr(os, 'readlink'):
        readlink = property(lambda self: os.readlink(self))
    if hasattr(os, 'fsencode'):
        fsencode = fsencoded = property(lambda self: os.fsencode(self))
    access = lambda self, mode, **kwargs: os.access(self, mode, **kwargs)
    if PY33:
        isreadable = property(lambda self: LazyObjectProxy(lambda **kwargs: os.access(self, os.R_OK, **kwargs)))
        iswritable = property(lambda self: LazyObjectProxy(lambda **kwargs: os.access(self, os.W_OK, **kwargs)))
        isexecutable = property(lambda self: LazyObjectProxy(lambda **kwargs: os.access(self, os.R_OK | os.X_OK, **kwargs)))
    else:
        isreadable = property(lambda self: os.access(self, os.R_OK))
        iswritable = property(lambda self: os.access(self, os.W_OK))
        isexecutable = property(lambda self: os.access(self, os.R_OK | os.X_OK))
    if hasattr(os, 'chroot'):
        chroot = lambda self: os.chroot(self)
    if hasattr(os, 'chflags'):
        chflags = lambda self, flags, follow_symlinks=True: os.chflags(self, flags) if follow_symlinks else os.lchflags(self, flags)
        lchflags = lambda self, flags: os.lchflags(self, flags)

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

    def chmod(self, mode, follow_symlinks=True, **kwargs):
        if follow_symlinks:
            return os.chmod(self, mode, **kwargs)
        else:
            if PY33:
                os.chmod(self, mode, follow_symlinks=follow_symlinks, **kwargs)
            else:
                os.lchmod(self, mode, **kwargs)

    def chown(self, uid, gid, follow_symlinks=True, **kwargs):
        if follow_symlinks:
            os.chown(self, uid, gid, **kwargs)
        else:
            if PY33:
                os.chown(self, uid, gid, follow_symlinks=follow_symlinks, **kwargs)
            else:
                os.lchown(self, uid, gid, **kwargs)

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
                return io.open(self, *open_args, **open_kwargs)
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


class ZipPath(AbstractPath):
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

    __div__ = __floordiv__ = __truediv__ = pathjoin = joinpath
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
