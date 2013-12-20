import shutil
import sys
import os
import tempfile
import zipfile
import stat
from functools import wraps
from six import reraise

class PathError(Exception):
    pass

class PathMustBeDirectory(PathError):
    pass

class PathMustBeFile(PathError):
    pass

class PathDoesNotExist(PathError):
    pass

def pth(path='.'):
    #print '#%r#' % path
    if zipfile.is_zipfile(path):
        return ZipPath(Path(path), zipfile.ZipFile(path))
    else:
        return Path(path)

identity = lambda x: x
attribute = lambda func, constructor=pth: property(lambda self: constructor(func(self)))
raw_attribute = property
nth_attribute = lambda func, position: property(lambda path: func(path)[position])
def pair_attribute(func, first_func=identity, second_func=identity):
    def pair_attribute_wrapper(self):
        first_value, second_value = func(self)
        return first_func(first_value), second_func(second_value)
    return property(pair_attribute_wrapper)

class Path(str):
    abs = abspath = attribute(os.path.abspath)
    name = basename = attribute(os.path.basename)
    commonprefix = os.path.commonprefix
    dir = dirname = attribute(os.path.dirname)
    exists = raw_attribute(os.path.exists)
    expanduser = attribute(os.path.expanduser)
    expandvars = attribute(os.path.expandvars)
    atime = getatime = raw_attribute(os.path.getatime)
    ctime = getctime = raw_attribute(os.path.getctime)
    mtime = getmtime = raw_attribute(os.path.getmtime)
    size = getsize = raw_attribute(os.path.getsize)
    isabs = raw_attribute(os.path.isabs)
    isdir = raw_attribute(os.path.isdir)
    isfile = raw_attribute(os.path.isfile)
    islink = raw_attribute(os.path.islink)
    ismount = raw_attribute(os.path.ismount)
    lexists = raw_attribute(os.path.lexists)
    normcase = attribute(os.path.normcase)
    normpath = attribute(os.path.normpath)
    realpath = attribute(os.path.realpath)
    relpath = os.path.relpath
    splitpath = pair_attribute(os.path.split, pth, pth)
    splitdrive = pair_attribute(os.path.splitdrive, identity, pth)
    splitext = pair_attribute(os.path.splitext, pth, identity)
    drive = nth_attribute(os.path.splitdrive, 0)
    ext = nth_attribute(os.path.splitext, 1)

    def __repr__(self):
        return '<Path %s>' % super(Path, self).__repr__()

    def __div__(self, path):
        return pth(os.path.join(self, path))

    def __iter__(self):
        if not self.isdir:
            raise PathMustBeDirectory("%r is not a directory nor a zip !" % self)

        for name in os.listdir(self):
            path = pth(os.path.join(self, name))
            yield path
            if path.isdir:
                for name in path:
                    yield name

    def __call__(self, *open_args, **open_kwargs):
        if self.isfile:
            return open(self, *open_args, **open_kwargs)
        else:
            raise PathMustBeFile("%r is not a file !" % self)

@property
def unavailable(self):
    raise AttributeError("Not available here.")

zippath_attribute = lambda func: property(lambda self: ZipPath(
    func(self._ZipPath__zippath),
    self._ZipPath__zipobj,
    self._ZipPath__relpath,
))
relpath_attribute = lambda func: property(lambda self: constructor(func(self)))

class ZipPath(Path):
    abs = abspath = attribute(os.path.abspath)
    name = basename = attribute(os.path.basename)
    commonprefix = os.path.commonprefix
    dir = dirname = attribute(os.path.dirname)
    @property
    def exists(self):
        path = self.__relpath.rstrip('/')
        if not path:
            return True
        try:
            self.__zipobj.getinfo(path)
        except KeyError as exc:
            try:
                self.__zipobj.getinfo(path)
            except KeyError as exc:
                return False
        return True
    expanduser = zippath_attribute(os.path.expanduser)
    expandvars = property(lambda self: ZipPath(
        os.path.expandvars(self.__zippath),
        self.__zipobj,
        os.path.expandvars(self.__relpath),
    ))
    atime = unavailable
    ctime = raw_attribute(os.path.getctime)
    mtime = unavailable
    @property
    def size(self):
        path = self.__relpath.rstrip('/')
        if not path:
            return self.__zippath.size
        try:
            zi = self.__zipobj.getinfo(path)
        except KeyError as exc:
            reraise(PathDoesNotExist, PathDoesNotExist(exc), sys.exc_info()[2])
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
        except KeyError as exc:
            return False
    @property
    def isfile(self):
        path = self.__relpath.rstrip('/')
        if not path:
            return False
        try:
            self.__zipobj.getinfo(path)
        except KeyError as exc:
            return False
        else:
            return True
    islink = raw_attribute(os.path.islink)
    ismount = raw_attribute(os.path.ismount)
    lexists = unavailable
    normcase = zippath_attribute(os.path.normcase)
    normpath = zippath_attribute(os.path.normpath)
    realpath = zippath_attribute(os.path.realpath)
    relpath = unavailable
    splitpath = pair_attribute(os.path.split, pth, pth)
    splitdrive = pair_attribute(os.path.splitdrive, identity, pth)
    splitext = pair_attribute(os.path.splitext, pth, identity)
    drive = nth_attribute(os.path.splitdrive, 0)
    ext = nth_attribute(os.path.splitext, 1)

    def __new__(cls, path, zipobj, relpath=""):
        if not zipfile.is_zipfile(path):
            return pth(os.path.join(path, relpath).rstrip('/'))
        obj = str.__new__(cls, os.path.join(path, relpath).rstrip('/'))
        obj.__zippath = path
        obj.__zipobj = zipobj
        obj.__relpath = relpath
        return obj

    def __repr__(self):
        return '<ZipPath %r / %r>' % (str(self.__zippath), self.__relpath)

    def __div__(self, path):
        return ZipPath(self.__zippath, self.__zipobj, self.__relpath)

    def __getitem__(self, name):
        if name == 'isdir':
            path = self.__relpath.rstrip('/')
            if not path:
                return True
            try:
                self.__zipobj.getinfo(path + '/')
            except KeyError as exc:
                return False
        elif name == 'isfile':
            path = self.__relpath.rstrip('/')
            if not path:
                return False
            try:
                self.__zipobj.getinfo(path)
            except KeyError as exc:
                return False
            else:
                return True
        elif name == 'size':
            path = self.__relpath.rstrip('/')
            if not path:
                return self.__zippath['size']
            try:
                zi = self.__zipobj.getinfo(path)
            except KeyError as exc:
                reraise(PathDoesNotExist, PathDoesNotExist(exc), sys.exc_info()[2])
            else:
                return zi.file_size
        else:
            raise KeyError("Unknown path attribute %r" % name)

    def __iter__(self):
        if not self['isdir']:
            raise PathMustBeDirectory("%r is not a directory !" % self)

        for name in self.__zipobj.namelist():
            if name.startswith(self.__relpath):
                yield ZipPath(self.__zippath, self.__zipobj, name)

    def __call__(self, *open_args, **open_kwargs):
        if self['isfile']:
            return self.__zipobj.open(self.__relpath, *open_args, **open_kwargs)
        else:
            raise PathMustBeFile("%r is not a file !" % self)

    def __div__(self, other):
        return ZipPath(self.__zippath, self.__zipobj, os.path.join(self.__relpath, str(other)))

class TempPath(Path):
    def __init__(self, **mkdtemp_kwargs):
        super(TmpDir, self).__init__(tempfile.mkdtemp(**mkdtemp_kwargs))

    def __enter__(self):
        return self

    def __exit__(self, tt=None, tv=None, tb=None):
        shutil.rmtree(str(self))


pth.Path = Path
pth.ZipPath = ZipPath
pth.TempPath = TempPath

if __name__ != '__main__':
    pth.__mod = sys.modules['pth'] # gotta do this, otherwise it gets garbage collected
    sys.modules['pth'] = pth
