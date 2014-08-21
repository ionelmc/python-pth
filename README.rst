==========================
        python-pth
==========================

.. image:: http://img.shields.io/travis/ionelmc/python-pth/master.png
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/ionelmc/python-pth

.. image:: https://ci.appveyor.com/api/projects/status/49hd684jo3y461oo/branch/master
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/ionelmc/python-pth

.. image:: http://img.shields.io/coveralls/ionelmc/python-pth/master.png
    :alt: Coverage Status
    :target: https://coveralls.io/r/ionelmc/python-pth

.. image:: http://img.shields.io/pypi/v/pth.png
    :alt: PYPI Package
    :target: https://pypi.python.org/pypi/pth

.. image:: http://img.shields.io/pypi/dm/pth.png
    :alt: PYPI Package
    :target: https://pypi.python.org/pypi/pth

**Note:** This is in very alpha state.

Simple and brief path traversal and filesystem access library. This library is a bit different that other path manipulation libraries:

* Path are subclasses of strings. You can use them anyhere you would use a string.
* Almost everything from ``os.path`` is available as a **property** with the same name except:

  * ``os.path.relpath`` is a **method**
  * ``os.path.getsize`` becomes a **property** named ``size``
  * ``os.path.getatime`` becomes a **property** named ``atime``
  * ``os.path.getctime`` becomes a **property** named ``ctime``
  * ``os.path.getmtime`` becomes a **property** named ``mtime``
  * ``os.path.split`` becomes a **method** name ``splitpath`` as ``split`` is already a string method
  * ``os.path.join`` becomes a **method** name ``joinpath`` as ``join`` is already a string method
  * ``os.path.commonprefix`` *is not implemented*
  * ``os.path.basename`` becomes a **property** named ``name``
  * ``os.path.dirname`` becomes a **property** named ``dir``
  * ``os.listdir`` becomes a **property** named ``list``
  * ``os.walk`` becomes a **property** named ``tree``

* Calling a *Path* object calls ``open()`` on the path. Takes any argument ``open`` would take (except the filename ofcourse).
* Transparent support for files in .zip files.

Basically it is designed for extreme brevity. It shares `Unipath <https://pypi.python.org/pypi/Unipath/>`_'s
str-subclassing approach and and it has seamless zip support (like Twisted's `ZipPath
<http://twistedmatrix.com/trac/browser/trunk/twisted/python/zippath.py>`_).

Usage
-----

Getting started::

    >>> import pth
    >>> pth  # the module is a function!
    <function pth at ...>
    >>> p = pth("a.txt")
    >>> p
    <Path 'a.txt'>
    >>> p
    <Path 'a.txt'>


API
---


============================= ================== ============================== ============================== ======================== =======
os/os.path/shutil             path.py            Unipath                        pth.Path                       pth.ZipPath support?     Notes
============================= ================== ============================== ============================== ======================== =======
os.path.abspath(p)            p.abspath()        p.absolute()                   ``p.abs``, ``p.abspath``       ✔                        Return absolute path.
os.path.basename(p)           p.name             p.name                         ``p.name``, ``p.basename``     ✔
os.path.commonprefix(p)       ―                  ―                              ―                              ✘                        Common prefix. [1]_
os.path.dirname(p)            p.parent           p.parent                       ``p.dirname``, ``p.dir``       ✔                        All except the last component.
os.path.exists(p)             p.exists()         fsp.exists()                   ``p.exists``                   ✔ 	                Does the path exist?
os.path.lexists(p)            p.lexists()        fsp.lexists()                  ``p.lexists``                  ✘                        Does the symbolic link exist?
os.path.expanduser(p)         p.expanduser()     p.expand_user()                ``p.expanduser``               ✔                        Expand "~" and "~user" prefix.
os.path.expandvars(p)         p.expandvars()     p.expand_vars()                ``p.expandvars``               ✔                        Expand "$VAR" environment variables.
os.path.getatime(p)           p.atime            fsp.atime()                    ``p.atime``                    ✘                        Last access time.
os.path.getmtime(p)           p.mtime            fsp.mtime()                    ``p.mtime``                    ✘                        Last modify time.
os.path.getctime(p)           p.ctime            fsp.ctime()                    ``p.ctime``                    ✔                        Platform-specific "ctime".
os.path.getsize(p)            p.size             fsp.size()                     ``p.size``                     ✔                        File size.
os.path.isabs(p)              p.isabs()          p.isabsolute                                                                           Is path absolute?
os.path.isfile(p)             p.isfile()         fsp.isfile()                                                                           Is a file?
os.path.isdir(p)              p.isdir()          fsp.isdir()                                                                            Is a directory?
os.path.islink(p)             p.islink()         fsp.islink()                                                                           Is a symbolic link?
os.path.ismount(p)            p.ismount()        fsp.ismount()                                                                          Is a mount point?
os.path.join(p, "Q/R")        p.joinpath("Q/R")  [FS]Path(p, "Q/R")                                                                     Join paths.
                                                 ―or-
                                                 p.child("Q", "R")
os.path.normcase(p)           p.normcase()       p.norm_case()                                                                          Normalize case.
os.path.normpath(p)           p.normpath()       p.norm()                                                                               Normalize path.
os.path.realpath(p)           p.realpath()       fsp.real_path()                                                                        Real path without symbolic links.
os.path.samefile(p, q)        p.samefile(q)      fsp.same_file(q)                                                                       True if both paths point to the same filesystem item.
os.path.sameopenfile(d1, d2)  ―                  ―
os.path.samestat(st1, st2)    ―                  ―
os.path.split(p)              p.splitpath()      (p.parent, p.name)                                                                     Split path at basename.
os.path.splitdrive(p)         p.splitdrive()     ―                                                                                      [2]_
os.path.splitext(p)           p.splitext()       ―                                                                                      [2]_
os.path.splitunc(p)           p.splitunc()       ―                                                                                      [2]_
os.path.walk(p, func, args)   ―                  ―                                                                                      [3]_
os.access(p, const)           p.access(const)    ―                                                                                      [4]_
os.chdir(d)                   ―                  fsd.chdir()                                                                            Change current directory.
os.fchdir(fd)                 ―                  ―                                                                                      [Not a path operation.]
os.getcwd()                   path.getcwd()      FSPath.cwd()                                                                           Get current directory.
os.chroot(d)                  d.chroot()         ―                                                                                      [5]_
os.chmod(p, 0644)             p.chmod(0644)      fsp.chmod(0644)                                                                        Change mode (permission bits).
os.chown(p, uid, gid)         p.chown(uid, gid)  fsp.chown(uid, gid)                                                                    Change ownership.
os.lchown(p, uid, gid)        ―                  ―                                                                                      [6]_
os.link(src, dst)             p.link(dst)        fsp.hardlink(dst)                                                                      Make hard link.
os.listdir(d)                 ―                  fsd.listdir(names_only=True)                                                           List directory; return base filenames.
os.lstat(p)                   p.lstat()          fsp.lstat()                                                                            Like stat but don't follow symbolic link.
os.mkfifo(p, 0666)            ―                  ―
os.mknod(p, ...)              ―                  ―
os.major(device)              ―                  ―
os.minor(device)              ―                  ―
os.makedev(...)               ―                  ―
os.mkdir(d, 0777)             d.mkdir(0777)      fsd.mkdir(mode=0777)                                                                   Create directory.
os.makedirs(d, 0777)          d.makedirs(0777)   fsd.mkdir(True, 0777)                                                                  Create a directory and necessary parent directories.
os.pathconf(p, name)          p.pathconf(name)   ―                                                                                      Return Posix path attribute.  (What the hell is this?)
os.readlink(l)                l.readlink()       fsl.read_link()                                                                        Return the path a symbolic link points to.
os.remove(f)                  f.remove()         fsf.remove()                                                                           Delete file.
os.removedirs(d)              d.removedirs()     fsd.rmdir(True)                                                                        Remove empty directory and all its empty ancestors.
os.rename(src, dst)           p.rename(dst)      fsp.rename(dst)                                                                        Rename a file or directory atomically (must be on same device).
os.renames(src, dst)          p.renames(dst)     fsp.rename(dst, True)                                                                  Combines os.rename, os.makedirs, and os.removedirs.
os.rmdir(d)                   d.rmdir()          fsd.rmdir()                                                                            Delete empty directory.
os.stat(p)                    p.stat()           fsp.stat()                                                                             Return a "stat" object.
os.statvfs(p)                 p.statvfs()        fsp.statvfs()                                                                          Return a "statvfs" object.
os.symlink(src, dst)          p.symlink(dst)     fsp.write_link(link_text)                                                              Create a symbolic link.                                                ("write_link" argument order is opposite from Python's!)
os.tempnam(...)               ―                  ―                                                                                      [7]_
os.unlink(f)                  f.unlink()         ―                                                                                      Same as .remove().
os.utime(p, times)            p.utime(times)     fsp.set_times(mtime, atime)                                                            Set access/modification times.
os.walk(...)                  ―                  ―                                                                                      [3]_
shutil.copyfile(src, dst)     f.copyfile(dst)    fsf.copy(dst, ...)                                                                     Copy file.  Unipath method is more than copyfile but less than copy2.
shutil.copyfileobj(...)       ―                  ―
shutil.copymode(src, dst)     p.copymode(dst)    fsp.copy_stat(dst, ...)                                                                Copy permission bits only.
shutil.copystat(src, dst)     p.copystat(dst)    fsp.copy_stat(dst, ...)                                                                Copy stat bits.
shutil.copy(src, dst)         f.copy(dst)        ―                                                                                      High-level copy a la Unix "cp".
shutil.copy2(src, dst)        f.copy2(dst)       ―                                                                                      High-level copy a la Unix "cp -p".
shutil.copytree(...)          d.copytree(...)    fsp.copy_tree(...)                                                                     Copy directory tree.  (Not implemented in Unipath 0.1.0.)
shutil.rmtree(...)            d.rmtree(...)      fsp.rmtree(...)                                                                        Recursively delete directory tree.  (Unipath has enhancements.)
shutil.move(src, dst)         p.move(dst)        fsp.move(dst)                                                                          Recursively move a file or directory, using os.rename() if possible.
A + B                         A + B              A+B                                                                                    Concatenate paths.
os.path.join(A, B)            A / B              [FS]Path(A, B)                                                                         Join paths.
                                                 ―or―
                                                 p.child(B)
-                             p.expand()         p.expand()                                                                             Combines expanduser, expandvars, normpath.
os.path.dirname(p)            p.parent           p.parent                                                                               Path without final component.
os.path.basename(p)           p.name             p.name                                                                                 Final component only.
[8]_                          p.namebase         p.stem                                                                                 Final component without extension.
[9]_                          p.ext              p.ext                                                                                  Extension only.
os.path.splitdrive(p)[0]      p.drive            ―                                                                                      [2]_
-                             p.stripext()       ―                                                                                      Strip final extension.
-                             p.uncshare         ―                                                                                      [2]_
-                             p.splitall()       p.components()                                                                         List of path components.  (Unipath has special first element.)
-                             p.relpath()        fsp.relative()                                                                         Relative path to current directory.
-                             p.relpathto(dst)   fsp.rel_path_to(dst)                                                                   Relative path to 'dst'.
-                             d.listdir()        fsd.listdir()                                                                          List directory, return paths.
-                             d.files()          fsd.listdir(filter=FILES)                                                              List files in directory, return paths.
-                             d.dirs()           fsd.listdir(filter=DIRS)                                                               List subdirectories, return paths.
-                             d.walk(...)        fsd.walk(...)                                                                          Recursively yield files and directories.
-                             d.walkfiles(...)   fsd.walk(filter=FILES)                                                                 Recursively yield files.
-                             d.walkdirs(...)    fsd.walk(filter=DIRS)                                                                  Recursively yield directories.
-                             p.fnmatch(pattern) -                                                                                      True if self.name matches glob pattern.
-                             p.glob(pattern)    ―                                                                                      Advanced globbing.
-                             f.open(mode)       ―                                                                                      Return open file object.
-                             f.bytes()          fsf.read_file("rb")                                                                    Return file contents in binary mode.
-                             f.write_bytes()    fsf.write_file(content, "wb")                                                          Replace file contents in binary mode.
-                             f.text(...)        fsf.read_file()                                                                        Return file content.  (Encoding args not implemented yet.)
-                             f.write_text(...)  fsf.write_file(content)                                                                Replace file content.  (Not all Orendorff args supported.)
-                             f.lines(...)       ―                                                                                      Return list of lines in file.
-                             f.write_lines(...) -                                                                                      Write list of lines to file.
-                             f.read_md5()       ―                                                                                      Calculate MD5 hash of file.
-                             p.owner            ―                                                                                      Advanded "get owner" operation.
-                             p.readlinkabs()    ―                                                                                      Return the path this symlink points to, converting to absolute path.
-                             p.startfile()      ―                                                                                      What the hell is this?

-                             ―                  p.split_root()                                                                         Unified "split root" method.
-                             ―                  p.ancestor(N)                                                                          Same as specifying .parent N times.
-                             ―                  p.child(...)                                                                           "Safe" way to join paths.
-                             ―                  fsp.needs_update(...)                                                                  True if self is missing or older than any of the other paths.
============================= ================== ============================== ============================== ======================== =======

::

    >>> p = pth('tests')
    >>> p
    <Path 'tests'>

Joining paths::

    >>> p/"a"/"b"/"c"/"d"
    <Path 'tests/a/b/c/d'>

    >>> p/"/root"
    <Path '/root'>

Properties::

    >>> p.abspath
    <Path '/.../tests'>

    >>> p2 = p/'b.txt'
    >>> p2
    <Path 'tests/b.txt'>

    >>> p.exists
    True

    >>> p2.isfile
    True

    >>> p2()
    <...'tests/b.txt'...mode...'r'...>

    >>> pth('bogus-doesnt-exist')()
    Traceback (most recent call last):
      ...
    pth.PathMustBeFile: [Errno 2] No such file or directory: ...

Looping over children, including files in .zip files::

    >>> for i in sorted([i for i in p.tree]): print(i)
    tests/a
    tests/a/a.txt
    tests/b.txt
    tests/test.zip
    tests/test.zip/1
    tests/test.zip/1/1.txt
    tests/test.zip/B.TXT
    tests/test.zip/a.txt

    >>> for i in sorted([i for i in p.files]): print(i)
    tests/b.txt

    >>> for i in sorted([i for i in p.dirs]): print(i)
    tests/a
    tests/test.zip

    >>> for i in sorted([i for i in p.list]): print(i)
    tests/a
    tests/b.txt
    tests/test.zip

    >>> list(pth('bogus-doesnt-exist').tree)
    Traceback (most recent call last):
      ...
    pth.PathMustBeDirectory: <Path 'bogus-doesnt-exist'> is not a directory nor a zip !


Trying to access inexisting property::

    >>> p.bogus
    Traceback (most recent call last):
    ...
    AttributeError: 'Path' object has no attribute 'bogus'

Automatic wrapping of zips::

    >>> p/'test.zip'
    <ZipPath 'tests/test.zip' / ''>

Other properties::

    >>> p.abspath
    <Path '/.../tests'>

    >>> p.abs
    <Path '/.../tests'>

    >>> p.basename
    <Path 'tests'>

    >>> p.abs.basename
    <Path 'tests'>

    >>> p.name
    <Path 'tests'>

    >>> p.dirname
    <Path ''>

    >>> p.dir
    <Path ''>

    >>> p.exists
    True

    >>> pth('~root').expanduser
    <Path '/root'>

    >>> pth('~/stuff').expanduser
    <Path '/home/.../stuff'>

    >>> p.expandvars
    <Path 'tests'>

    >>> type(p.atime)
    <... 'float'>

    >>> type(p.ctime)
    <... 'float'>

    >>> type(p.size)
    <... 'int'>

    >>> p.isabs
    False

    >>> p.abs.isabs
    True

    >>> p.isdir
    True

    >>> p.isfile
    False

    >>> p.islink
    False

    >>> p.ismount
    False

    >>> p.lexists
    True

    >>> p.normcase
    <Path 'tests'>

    >>> p.normpath
    <Path 'tests'>

    >>> p.realpath
    <Path '/.../tests'>

    >>> p.splitpath
    (<Path ''>, <Path 'tests'>)

    >>> pth('a/b/c/d').splitpath
    (<Path 'a/b/c'>, <Path 'd'>)

    >>> pth('a/b/c/d').parts
    [<Path 'a'>, <Path 'b'>, <Path 'c'>, <Path 'd'>]

    >>> pth('/a/b/c/d').parts
    [<Path '/'>, <Path 'a'>, <Path 'b'>, <Path 'c'>, <Path 'd'>]

    >>> pth(*pth('/a/b/c/d').parts)
    <Path '/a/b/c/d'>

    >>> p.splitdrive
    ('', <Path 'tests'>)

    >>> p.drive
    ''

    >>> [i for i in (p/'xxx').tree]
    Traceback (most recent call last):
    ...
    pth.PathMustBeDirectory: <Path 'tests/xxx'> is not a directory nor a zip !

    >>> (p/'xxx').isfile
    False

    >>> (p/'xxx')()
    Traceback (most recent call last):
    ...
    pth.PathMustBeFile: ... 2...

    >>> p()
    Traceback (most recent call last):
    ...
    pth.PathMustBeFile: <Path 'tests'> is not a file !

    >>> pth('a.txt').splitext
    (<Path 'a'>, '.txt')

    >>> pth('a.txt').ext
    '.txt'


Zip stuff::

    >>> z = pth('tests/test.zip')
    >>> z
    <ZipPath 'tests/test.zip' / ''>

    >>> z.abspath
    <ZipPath '/.../tests/test.zip' / ''>

    >>> z.abs
    <ZipPath '/.../tests/test.zip' / ''>

    >>> z.basename # transforms in normal path cauze zip is not accessible in current dir
    <Path 'test.zip'>

    >>> z.abs.basename # transforms in normal path cauze zip is not accessible in current dir
    <Path 'test.zip'>

    >>> import os
    >>> os.chdir('tests')
    >>> z.basename
    <ZipPath 'test.zip' / ''>
    >>> z.name
    <ZipPath 'test.zip' / ''>
    >>> os.chdir('..')

    >>> z.dirname
    <Path 'tests'>

    >>> z.abs.dirname
    <Path '/.../tests'>

    >>> z.dir
    <Path 'tests'>

    >>> z.exists
    True

    >>> pth('~root').expanduser
    <Path '/root'>

    >>> pth('~/stuff').expanduser
    <Path '/home/.../stuff'>

    >>> z.expandvars
    <ZipPath 'tests/test.zip' / ''>

    >>> type(z.atime)
    Traceback (most recent call last):
    ...
    AttributeError: Not available here.

    >>> type(z.ctime)
    <... 'float'>

    >>> type(z.size)
    <... 'int'>

    >>> z.isabs
    False

    >>> z.abs.isabs
    True

    >>> z.isdir
    True

    >>> z.isfile
    False

    >>> z.islink
    False

    >>> z.ismount
    False

    >>> z.lexists
    Traceback (most recent call last):
    ...
    AttributeError: Not available here.

    >>> for i in z.tree: print((str(i), repr(i)))
    ('tests/test.zip/1',...... "<ZipPath 'tests/test.zip' / '1/'>")
    ('tests/test.zip/1/1.txt', "<ZipPath 'tests/test.zip' / '1/1.txt'>")
    ('tests/test.zip/B.TXT',..."<ZipPath 'tests/test.zip' / 'B.TXT'>")
    ('tests/test.zip/a.txt',..."<ZipPath 'tests/test.zip' / 'a.txt'>")

    >>> for i in z.files: print((str(i), repr(i)))
    ('tests/test.zip/B.TXT',..."<ZipPath 'tests/test.zip' / 'B.TXT'>")
    ('tests/test.zip/a.txt',..."<ZipPath 'tests/test.zip' / 'a.txt'>")

    >>> for i in z.dirs: print((str(i), repr(i)))
    ('tests/test.zip/1',...... "<ZipPath 'tests/test.zip' / '1/'>")

    >>> for i in z.list: print((str(i), repr(i)))
    ('tests/test.zip/1',...... "<ZipPath 'tests/test.zip' / '1/'>")
    ('tests/test.zip/B.TXT',..."<ZipPath 'tests/test.zip' / 'B.TXT'>")
    ('tests/test.zip/a.txt',..."<ZipPath 'tests/test.zip' / 'a.txt'>")

    >>> (z/'B.TXT')
    <ZipPath 'tests/test.zip' / 'B.TXT'>

    >>> str(z/'B.TXT')
    'tests/test.zip/B.TXT'

    >>> (z/'B.TXT').dirname
    <ZipPath 'tests/test.zip' / ''>

    >>> (z/'B.TXT').rel(z)
    <Path 'B.TXT'>

    >>> z.rel(z/'B.TXT')
    <Path '..'>

    >>> (z/'B.TXT').exists
    True

    >>> (z/'B.TXT').normcase
    <ZipPath 'tests/test.zip' / 'B.TXT'>

    >>> (z/'B.TXT').normpath
    <ZipPath 'tests/test.zip' / 'B.TXT'>

    >>> (z/'B.TXT').name
    <Path 'B.TXT'>

    >>> (z/'B.TXT').name
    <Path 'B.TXT'>

    >>> z.normcase
    <ZipPath 'tests/test.zip' / ''>

    >>> z.normpath
    <ZipPath 'tests/test.zip' / ''>

    >>> z.realpath
    <ZipPath '/.../tests/test.zip' / ''>

    >>> z.splitpath
    (<Path 'tests'>, <Path 'test.zip'>)

    >>> z.splitdrive
    ('', <ZipPath 'tests/test.zip' / ''>)

    >>> z.drive
    ''

    >>> pth('a.txt').splitext
    (<Path 'a'>, '.txt')

    >>> pth('a.txt').ext
    '.txt'

Working with files in a .zip::

    >>> p = z/'B.TXT'
    >>> p.abspath
    <ZipPath '/.../tests/test.zip' / 'B.TXT'>

    >>> p.abs
    <ZipPath '/.../tests/test.zip' / 'B.TXT'>

    >>> p.basename
    <Path 'B.TXT'>

    >>> p.abs.basename
    <Path 'B.TXT'>

    >>> p.name
    <Path 'B.TXT'>

    >>> p.dirname
    <ZipPath 'tests/test.zip' / ''>

    >>> p.dir
    <ZipPath 'tests/test.zip' / ''>

    >>> p.exists
    True

    >>> type(p.atime)
    Traceback (most recent call last):
    ...
    AttributeError: Not available here.

    >>> type(p.ctime)
    <... 'float'>

    >>> type(p.size)
    <... 'int'>

    >>> p.isabs
    False

    >>> p.abs.isabs
    True

    >>> p.isdir
    False

    >>> p.isfile
    True

    >>> p.islink
    False

    >>> p.ismount
    False

    >>> p.lexists
    Traceback (most recent call last):
    ...
    AttributeError: Not available here.

    >>> p.normcase
    <ZipPath 'tests/test.zip' / 'B.TXT'>

    >>> p.normpath
    <ZipPath 'tests/test.zip' / 'B.TXT'>

    >>> p.realpath
    <ZipPath '/.../tests/test.zip' / 'B.TXT'>

    >>> p.splitpath
    (<ZipPath 'tests/test.zip' / ''>, <Path 'B.TXT'>)

    >>> pth.ZipPath.from_string('tests/test.zip/1/1.txt')
    <ZipPath 'tests/test.zip' / '1/1.txt'>

    >>> p.splitdrive
    ('', <ZipPath 'tests/test.zip' / 'B.TXT'>)

    >>> p.drive
    ''

    >>> p.splitext
    (<ZipPath 'tests/test.zip' / 'B'>, '.TXT')

    >>> p.ext
    '.TXT'

    >>> p.joinpath('tete')
    <ZipPath 'tests/test.zip' / 'B.TXT/tete'>

    >>> p.joinpath('tete').exists
    False

    >>> p.joinpath('tete').isdir
    False

    >>> p.joinpath('tete').isfile
    False

    >>> p.joinpath('tete').ctime
    Traceback (most recent call last):
    ...
    pth.PathDoesNotExist: "There is no item named 'B.TXT/tete' in the archive"

    >>> p.joinpath('tete').size
    Traceback (most recent call last):
    ...
    pth.PathDoesNotExist: "There is no item named 'B.TXT/tete' in the archive"

    >>> p.relpath('tests')
    <Path 'test.zip/B.TXT'>

    >>> p.joinpath('tete')('rb')
    Traceback (most recent call last):
    ...
    pth.PathMustBeFile: <ZipPath 'tests/test.zip' / 'B.TXT/tete'> is not a file !

    >>> p('r')
    <zipfile.ZipExtFile ...>

    >>> [i for i in p.tree]
    Traceback (most recent call last):
    ...
    pth.PathMustBeDirectory: <ZipPath 'tests/test.zip' / 'B.TXT'> is not a directory !

    >>> z('rb')
    Traceback (most recent call last):
    ...
    pth.PathMustBeFile: <ZipPath 'tests/test.zip' / ''> is not a file !

Iterating though the contents of the zip::

    >>> [i for i in z.tree]
    [<ZipPath 'tests/test.zip' / '1/'>, <ZipPath 'tests/test.zip' / '1/1.txt'>, <ZipPath 'tests/test.zip' / 'B.TXT'>, <ZipPath 'tests/test.zip' / 'a.txt'>]

    >>> [i for i in z.files]
    [<ZipPath 'tests/test.zip' / 'B.TXT'>, <ZipPath 'tests/test.zip' / 'a.txt'>]

    >>> [i for i in z.dirs]
    [<ZipPath 'tests/test.zip' / '1/'>]

Note that there's this inconsistency with joining absolute paths::

    >>> z/pth('/root')
    <Path '/root'>

Vs::

    >>> z/'/root'
    <ZipPath 'tests/test.zip' / '/root'>

TODO: Make this nicer.

::

    >>> pth.ZipPath('tests', '', '')
    <Path 'tests'>

    >>> pth.ZipPath.from_string('/bogus/path/to/stuff/bla/bla/bla')
    <Path '/bogus/path/to/stuff/bla/bla/bla'>

    >>> pth.ZipPath.from_string('bogus')
    <Path 'bogus'>

    >>> pth.ZipPath.from_string('tests/test.zip/bogus/path/to/stuff/bla/bla/bla')
    <ZipPath 'tests/test.zip' / 'bogus/path/to/stuff/bla/bla/bla'>

    >>> pth.ZipPath.from_string('tests/1/bogus/path/to/stuff/bla/bla/bla')
    <Path 'tests/1/bogus/path/to/stuff/bla/bla/bla'>

    >>> pth.ZipPath.from_string('tests')
    <Path 'tests'>

    >>> pth.ZipPath.from_string('tests/bogus')
    <Path 'tests/bogus'>

And there's a *temporary path*::

    >>> t = pth.TempPath()
    >>> t
    <TempPath '/tmp/...'>

    >>> with t:
    ...     with (t/"booo.txt")('w+') as f:
    ...         _ = f.write("test")
    ...     print([i for i in t.tree])
    [<Path '/tmp/.../booo.txt'>]

    >>> t.exists
    False
