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

* Iterating through a *Path* object yields *Path* instances for all the children in the tree. This is equivalent to ``os.walk`` but without
  having to do all that manual wrapping (it's so annoying !).
* Calling a *Path* object calls ``open()`` on the path. Takes any argument ``open`` would take (except the filename ofcourse).


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

    >>> p/"a"/"b"/"c"/"d"
    <Path 'tests/a/b/c/d'>

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
    <open file 'tests/b.txt', mode 'r' at ...>

    >>> for i in p: print i
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

    >>> p.bogus
    Traceback (most recent call last):
    ...
    AttributeError: 'Path' object has no attribute 'bogus'

    >>> p/'test.zip'
    <ZipPath 'tests/test.zip' / ''>

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

    >>> type(p.getatime)
    <type 'float'>

    >>> type(p.atime)
    <type 'float'>

    >>> type(p.getctime)
    <type 'float'>

    >>> type(p.ctime)
    <type 'float'>

    >>> type(p.getsize)
    <type 'int'>

    >>> type(p.size)
    <type 'int'>

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

    >>> type(z.getatime)
    <type 'float'>

    >>> type(z.atime)
    Traceback (most recent call last):
    ...
    AttributeError: Not available here.

    >>> type(z.getctime)
    <type 'float'>

    >>> type(z.ctime)
    <type 'float'>

    >>> type(z.getsize)
    <type 'int'>

    >>> type(z.size)
    <type 'int'>

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

    >>> for i in z: print i, repr(i)
    tests/test.zip/1...... <ZipPath 'tests/test.zip' / '1/'>
    tests/test.zip/1/1.txt <ZipPath 'tests/test.zip' / '1/1.txt'>
    tests/test.zip/B.TXT...<ZipPath 'tests/test.zip' / 'B.TXT'>
    tests/test.zip/a.txt...<ZipPath 'tests/test.zip' / 'a.txt'>

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
