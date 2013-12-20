==========================
        python-pth
==========================

Simple and brief path traversal and filesystem access library. This library is a bit different that other path manipulation libraries:

* Path are subclasses of strings. You can use them anyhere you would use a string.
* Almost everything from ``os.path`` is available as a **property** with the same name except:

  * ``relpath`` and ``commonprefix`` are methods
  * ``getsize`` becomes a property named ``size``
  * ``getatime`` becomes a property named ``atime``
  * ``getctime`` becomes a property named ``ctime``
  * ``getmtime`` becomes a property named ``mtime``
  * ``split`` becomes a method name ``splitpath`` as ``split`` is already a string method
  * ``join`` becomes a method name ``joinpath`` as ``join`` is already a string method
  * ``commonprefix`` is not implemented

* Iterating through a *Path* object yields *Path* instances for all the children in the tree. This is equivalent to ``os.walk`` but without
  having to do all that manual wrapping (it's so annoying !).
* Calling a *Path* object calls ``open()`` on the path. Takes any argument ``open`` would take (except the filename ofcourse).
* Transparent support for files in .zip files.

Usage
-----

Getting started::

    >>> import pth
    >>> pth
    <function pth at ...>
    >>> p = pth("a.txt")
    >>> p
    <Path 'a.txt'>
    >>> p
    <Path 'a.txt'>


Doctests
--------

::

    >>> import pth

    >>> p = pth('tests')
    >>> p
    <Path 'tests'>

Joining paths::

    >>> p/"a"/"b"/"c"/"d"
    <Path 'tests/a/b/c/d'>

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

Looping over children, including files in .zip files::

    >>> for i in p: print(i)
    tests/test_pth.pyc
    tests/a
    tests/a/a.txt
    tests/test_pth.py
    tests/test.zip
    tests/test.zip/1
    tests/test.zip/1/1.txt
    tests/test.zip/B.TXT
    tests/test.zip/a.txt
    tests/b.txt

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

    >>> p.splitdrive
    ('', <Path 'tests'>)

    >>> p.drive
    ''

    >>> [i for i in p/'xxx']
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

    >>> for i in z: print((str(i), repr(i)))
    ('tests/test.zip/1',...... "<ZipPath 'tests/test.zip' / '1/'>")
    ('tests/test.zip/1/1.txt', "<ZipPath 'tests/test.zip' / '1/1.txt'>")
    ('tests/test.zip/B.TXT',..."<ZipPath 'tests/test.zip' / 'B.TXT'>")
    ('tests/test.zip/a.txt',..."<ZipPath 'tests/test.zip' / 'a.txt'>")

    >>> (z/'B.TXT')
    <ZipPath 'tests/test.zip' / 'B.TXT'>

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
    Traceback (most recent call last):
    ...
    AttributeError: Not available here.

    >>> p.joinpath('tete')('rb')
    Traceback (most recent call last):
    ...
    pth.PathMustBeFile: <ZipPath 'tests/test.zip' / 'B.TXT/tete'> is not a file !

    >>> p('r')
    <zipfile.ZipExtFile ...>

    >>> [i for i in p]
    Traceback (most recent call last):
    ...
    pth.PathMustBeDirectory: <ZipPath 'tests/test.zip' / 'B.TXT'> is not a directory !

    >>> z('rb')
    Traceback (most recent call last):
    ...
    pth.PathMustBeFile: <ZipPath 'tests/test.zip' / ''> is not a file !

    >>> [i for i in z]
    [<ZipPath 'tests/test.zip' / '1/'>, <ZipPath 'tests/test.zip' / '1/1.txt'>, <ZipPath 'tests/test.zip' / 'B.TXT'>, <ZipPath 'tests/test.zip' / 'a.txt'>]

    >>> pth.ZipPath('tests', '', '')
    <Path 'tests'>

    >>> t = pth.TempPath()
    >>> t
    <TempPath '/tmp/...'>

    >>> with t:
    ...     with (t/"booo.txt")('w+') as f:
    ...         _ = f.write("test")
    ...     print([i for i in t])
    [<Path '/tmp/.../booo.txt'>]

    >>> t.exists
    False

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

