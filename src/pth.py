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

identity = lambda x: x
attribute = lambda func: lambda path: pth(func(path))
raw_attribute = lambda func: lambda path: func(path)
nth_attribute = lambda func, position: lambda path: func(path)[position]
def pair_attribute(func, first_func=identity, second_func=identity):
    def pair_attribute_wrapper(path):
        first_value, second_value = func(path)
        return first_func(first_value), second_func(second_value)
    return pair_attribute_wrapper

def pth(path='.'):
    if zipfile.is_zipfile(path):
        return ZipPath(path, zipfile.ZipFile(path))
    else:
        return Path(path)

class Path(object):
    __slots__ = ('_Path__value', '_Path__attributes')
    __attributes = dict(
        abspath = attribute(os.path.abspath),
        abs = attribute(os.path.abspath),
        basename = attribute(os.path.basename),
        name = attribute(os.path.basename),
        dirname = attribute(os.path.dirname),
        dir = attribute(os.path.dirname),
        exists = raw_attribute(os.path.exists),
        expanduser = attribute(os.path.expanduser),
        expandvars = attribute(os.path.expandvars),
        getatime = raw_attribute(os.path.getatime),
        atime = raw_attribute(os.path.getatime),
        getctime = raw_attribute(os.path.getctime),
        ctime = raw_attribute(os.path.getctime),
        getsize = raw_attribute(os.path.getsize),
        size = raw_attribute(os.path.getsize),
        isabs = raw_attribute(os.path.isabs),
        isdir = raw_attribute(os.path.isdir),
        isfile = raw_attribute(os.path.isfile),
        islink = raw_attribute(os.path.islink),
        ismount = raw_attribute(os.path.ismount),
        lexists = raw_attribute(os.path.lexists),
        normcase = attribute(os.path.normcase),
        normpath = attribute(os.path.normpath),
        realpath = attribute(os.path.realpath),
        split = pair_attribute(os.path.split, pth, pth),
        splitdrive = pair_attribute(os.path.splitdrive, identity, pth),
        splitext = pair_attribute(os.path.splitext, pth, identity),
        drive = nth_attribute(os.path.splitdrive, 0),
        ext = nth_attribute(os.path.splitext, 1),
    )

    def __init__(self, path):
        self.__value = path

    def __str__(self):
        return self.__value

    def __repr__(self):
        return '<Path %r>' % self.__value

    def __getattr__(self, path):
        return pth(os.path.join(self.__value, path))

    def __getitem__(self, name):
        try:
            return self.__attributes[name](self.__value)
        except KeyError as exc:
            raise KeyError("Unknown path attribute %r" % name)

    def __iter__(self):
        if not self['isdir']:
            raise PathMustBeDirectory("%r is not a directory nor a zip !" % self)

        for name in os.listdir(self.__value):
            path = pth(os.path.join(self.__value, name))
            yield path
            if path['isdir']:
                for name in path:
                    yield name

    def __call__(self, *open_args, **open_kwargs):
        if self['isfile']:
            return open(self.__value, *open_args, **open_kwargs)
        else:
            raise PathMustBeFile("%r is not a file !" % self)

    def __div__(self, other):
        return pth(os.path.join(self.__value, str(other)))

    def __invert__(self):
        return pth(os.path.expanduser("~" + self.__value))

class ZipPath(object):
    __slots__ = '__zippath', '__zipobj', '__relpath', '__attributes'

    def __init__(self, path, zipobj, relpath=""):
        self.__zippath = path
        self.__zipobj = zipobj
        self.__relpath = relpath

    def __str__(self):
        return os.path.join(self.__zippath, self.__relpath)

    def __repr__(self):
        return '<ZipPath %r / %r>' % (self.__zippath, self.__relpath)

    def __getattr__(self, path):
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
else:
    import doctest
    print doctest.testmod(optionflags=doctest.ELLIPSIS)
    #
    #class A(object):
    #    __tete = 2
    #    def __init__(self):
    #        self.__bubububu_ = 1
    #        print self.__dict__
    #        print pth.__dict
    #class B(A):
    #    pass
    #
    #a, b = A(), B()
    #print a.__dict__, b.__dict__
    #print a.__A_bubu, b.__A_bubu
