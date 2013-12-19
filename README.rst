==========================
        python-pth
==========================

Simple and brief path traversal and filesystem access library. This library is a bit different that other path manipulation libraries:

* There are **no methods**. Attributes return new *Path* istances - syntactic sugar for ``os.path.join``. Why ? ``os.path.join`` is the most
  used function from ``os.path`` by far. Most names don't have extensions.
* The unary functions from ``os.path`` (the ones that take a single argument) are available as object *items*. Eg:
  ``pth('a.txt')['exists']``
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

    >>> p.a.b.c.d
    <Path 'tests/a/b/c/d'>

    >>> p['abs']
    <Path '/.../tests'>

    >>> p2 = p/'b.txt'
    >>> p2
    <Path 'tests/b.txt'>

    >>> p['exists']
    True

    >>> p2['isfile']
    True

    >>> p2()
    <open file 'tests/b.txt', mode 'r' at ...>

    >>> for i in p: print i
    tests/test_pth.pyc
    tests/a
    tests/a/a.txt
    tests/test_pth.py
    tests/test.zip/
    tests/test.zip/1/
    tests/test.zip/1/1.txt
    tests/test.zip/b.txt
    tests/test.zip/a.txt
    tests/b.txt

    >>> p['bogus']
    Traceback (most recent call last):
    ...
    KeyError: "Unknown path attribute 'bogus'"

    >>> p/'test.zip'
    <ZipPath 'tests/test.zip' / ''>

    >>> p['abspath']
    <Path '/.../tests'>

    >>> p['abs']
    <Path '/.../tests'>

    >>> p['basename']
    <Path 'tests'>

    >>> p['abs']['basename']
    <Path 'tests'>

    >>> p['name']
    <Path 'tests'>

    >>> p['dirname']
    <Path ''>

    >>> p['dir']
    <Path ''>

    >>> p['exists']
    True

    >>> pth('~root')['expanduser']
    <Path '/root'>

    >>> pth('~/stuff')['expanduser']
    <Path '/home/.../stuff'>

    >>> p['expandvars']
    <Path 'tests'>

    >>> type(p['getatime'])
    <type 'float'>

    >>> type(p['atime'])
    <type 'float'>

    >>> type(p['getctime'])
    <type 'float'>

    >>> type(p['ctime'])
    <type 'float'>

    >>> type(p['getsize'])
    <type 'int'>

    >>> type(p['size'])
    <type 'int'>

    >>> p['isabs']
    False

    >>> p['abs']['isabs']
    True

    >>> p['isdir']
    True

    >>> p['isfile']
    False

    >>> p['islink']
    False

    >>> p['ismount']
    False

    >>> p['lexists']
    True

    >>> p['normcase']
    <Path 'tests'>

    >>> p['normpath']
    <Path 'tests'>

    >>> p['realpath']
    <Path '/.../tests'>

    >>> p['split']
    (<Path ''>, <Path 'tests'>)

    >>> p['splitdrive']
    ('', <Path 'tests'>)

    >>> p['drive']
    ''

    >>> pth('a.txt')['splitext']
    (<Path 'a'>, '.txt')

    >>> pth('a.txt')['ext']
    '.txt'
