==========
python-pth
==========

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

.. note::

    This is in very alpha state.

    And probably as far as it goes as it turns out it has a lot in common with
    `PEP-355 <http://legacy.python.org/dev/peps/pep-0355/>`_.

Simple and brief path traversal and filesystem access library. This library is a bit different that other path
manipulation libraries - the principles of this library:

* Path are subclasses of strings. You can use them anyhere you would use a string.
* All the function that works with paths from ``os`` / ``os.path`` / ``shutil`` should be available.
* Transparent support for files in .zip files (with limited functionality).
* Readonly functions are available as properties **property**. If the function would have side-effects (``chdir``,
  ``chroot`` etc) then it will be a method.
* Original names of the functions are kept. [1]
* Shorthands and brief aliases. Example:

  * ``os.path.getsize`` becomes a **property** named ``size``
  * ``os.path.getatime`` becomes a **property** named ``atime``
  * ``os.path.getctime`` becomes a **property** named ``ctime``
  * ``os.path.getmtime`` becomes a **property** named ``mtime``
  * ``os.path.basename`` becomes a **property** named ``name``
  * ``os.path.dirname`` becomes a **property** named ``dir``
  * ``os.listdir`` becomes a **property** named ``list``

  * Calling a *Path* object calls ``open()`` on the path. Takes any argument ``open`` would take (except the filename
    ofcourse).

.. [1]

  However there are few exceptions:

  * ``os.walk`` becomes a **property** named ``tree``
  * ``os.path.split`` becomes a **method** name ``splitpath`` as ``split`` is already a string method
  * ``os.path.join`` becomes a **method** name ``joinpath`` as ``join`` is already a string method


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

.. list-table::
    :header-rows: 1
    :widths: 10 10 10 70

    +   - ``os``/``os.path``/``shutil``
        - ``pth.Path``
        - ``pth.ZipPath`` support?
        - Notes
    +   - ``os.access(p, mode)``
        - ``p.access(mode)``
        - ✖
        - Test access with given mode.
    +   - ``os.access(p, os.R_OK)``
        - ``p.isreadable``

          or

          ``p.isreadable(
          dir_fd=None, effective_ids=False, follow_symlinks=True)`` (Python>=3.3)
        - ✖
        - Test read access.
    +   - ``os.access(p, os.W_OK)``
        - ``p.iswritable``

          or

          ``p.iswritable(
          dir_fd=None, effective_ids=False, follow_symlinks=True)`` (Python>=3.3)
        - ✖
        - Test write access.
    +   - ``os.access(p, os.R_OK|os.X_OK)``
        - ``p.isexecutable``

          or

          ``p.isexecutable(
          dir_fd=None, effective_ids=False, follow_symlinks=True)`` (Python>=3.3)
        - ✖
        - Test execute access.
    +   - ``os.chdir(p)``
        - ``p.cd()``

          or

          ``with p.cd:``

          or

          ``with p.cd():``
        - ✖
        - Change current directory.
    +   - ``os.chflags(p, flags)``
        - ``p.chflags(flags)``
        - ✖
        - Change path flags.
    +   - ``os.chmod(p, 0644)``
        - ``p.chmod(0644)``
        - ✖
        - Change mode (permission bits).
    +   - ``os.chown(p, uid, gid)``
        - ``p.chown(uid, gid)``
        - ✖
        - Change ownership.
    +   - ``os.chroot(p)``
        - ``p.chroot()``
        - ✖
        - Change the root directory of the current process.
    +   - ``os.getcwd()``
        - ``pth().abs``

          or

          ``pth.cwd``
        - ―
        - Get current directory.
    +   - ``os.fsencode(p)``
        - ``p.fsencode``

          or

          ``p.fsencoded``
        - ✖
        - Encode path to filesystem encoding.
    +   - ``os.fsdecode(p)``
        - ``pth(os.fsdecode(p))``
        - ✖
        - Decode path in filesystem encoding.
    +   - ``os.get_exec_path(env=None)``
        - ✖
        - ✖
        - Returns the list of paths from $PATH.
    +   - ``os.lchflags(p, flags)``
        - ``p.lchflags(flags)``

          or

          ``p.chflags(flags, follow_symlinks=False)``
        - ✖
        - Change path flags.
    +   - ``os.lchmod(p, 0644)``
        - ``p.lchmod(0644)``, ``p.chmod(0644, follow_symlinks=False)``
        - ✖
        - Change mode (permission bits) without following symlinks.
    +   - ``os.lchown(p, uid, gid)``
        - ``p.lchown(uid, gid)``, ``p.chown(uid, gid, follow_symlinks=False)``
        - ✖
        - Change ownership without following symlinks.
    +   - ``os.link(src, dst)``
        - ``p.link(dst)``
        - ✖
        - Make hard link.
    +   - ``os.link(src, dst, follow_symlinks=False)`` (Python>=3.3)
        - ``p.link(dst, follow_symlinks=False)`` (Python>=3.3 only)
        - ✖
        - Make hard link.
    +   - ``os.listdir(d)``
        - ``p.list``
        - ✔
        - List directory; return base filenames.
    +   - ``os.lstat(p)``
        - ``p.lstat()``
        - ✖
        - Like stat but don't follow symbolic link.
    +   - ``os.mkdir(d, 0777)``
        - ``d.mkdir(0777)``
        - ✖
        - Create directory.
    +   - ``os.makedirs(d, 0777)``
        - ``d.makedirs(0777)``
        - ✖
        - Create a directory and necessary parent directories.
    +   - ``os.mkfifo(path, mode=0o666, dir_fd=None)``
        - ``d.mkfifo(mode=0o666, dir_fd=None)``
        - ✖
        - Create a FIFO (a named pipe).
    +   - ``os.open(path, ...)``
        - ✖
        - ✖
        - Low-level file open (returns fd).
    +   - ``os.pathconf(p, name)``
        - ``p.pathconf(name)``
        - ✖
        - Return Posix path attribute.
    +   - ``os.path.abspath(p)``
        - ``p.abs``, ``p.abspath``
        - ✔
        - Returns an absolute path.
    +   - ``os.path.basename(p)``
        - ``p.name``, ``p.basename``
        - ✔
        - The last component.
    +   - ``os.path.commonprefix(p)``
        - ✖
        - ✖
        - Common prefix that can generate invalid paths.
    +   - ``os.path.dirname(p)``
        - ``p.dirname``, ``p.dir``
        - ✔
        - All except the last component.
    +   - ``os.path.exists(p)``
        - ``p.exists``
        - ✔
        - Does the path exist?
    +   - ``os.path.lexists(p)``
        - ``p.lexists``
        - ✖
        - Does the symbolic link exist?
    +   - ``os.path.expanduser(p)``
        - ``p.expanduser``
        - ✔
        - Expand "~" and "~user" prefix.
    +   - ``os.path.expandvars(p)``
        - ``p.expandvars``
        - ✔
        - Expand "$VAR" environment variables.
    +   - ``os.path.getatime(p)``
        - ``p.atime``
        - ✖
        - Last access time.
    +   - ``os.path.getmtime(p)``
        - ``p.mtime``
        - ✖
        - Last modify time.
    +   - ``os.path.getctime(p)``
        - ``p.ctime``
        - ✔
        - Platform-specific "ctime".
    +   - ``os.path.getsize(p)``
        - ``p.size``
        - ✔
        - File size.
    +   - ``os.path.isabs(p)``
        - ``p.isabs``
        - ✔
        - Is path absolute?
    +   - ``os.path.isfile(p)``
        - ``p.isfile``
        - ✔
        - Is a file?
    +   - ``os.path.isdir(p)``
        - ``p.isdir``
        - ✔
        - Is a directory?
    +   - ``os.path.islink(p)``
        - ``p.islink``
        - ✔
        - Is a symbolic link?
    +   - ``os.path.ismount(p)``
        - ``p.ismount``
        - ✔
        - Is a mount point?
    +   - ``os.path.join(p, "foobar")``
        - ``p / "foobar"``

          or

          ``p.joinpath(
          "foobar")``

          or

          ``p.pathjoin(
          "foobar")``
        - ✔
        - Join paths.
    +   - ``os.path.normcase(p)``
        - ``p.normcase``
        - ✔
        - Normalize case.
    +   - ``os.path.normpath(p)``
        - ``p.normpath``
        - ✔
        - Normalize path.
    +   - ``os.path.normcase(
          os.path.normpath(p))``
        - ``p.norm``
        - ✔
        - Normalize case and path.
    +   - ``os.path.relpath(p, q)``
        - ``p.rel(q)``

          or

          ``p.relpath(q)``
        - ✔
        - Relative path.
    +   - ``os.path.realpath(p)``
        - ``p.real``

          or

          ``p.realpath``
        - ✔
        - Real path without symbolic links.
    +   - ``os.path.samefile(p, q)``
        - ``p.same(q)``

          or

          ``p.samefile(q)``
        - ✔
        - True if both paths point to the same filesystem item.
    +   - ``os.path.split(p)``
        - ``(p.parent, p.name)``

          or

          ``p.splitpath``

          or

          ``p.pathsplit``
        - ✔
        - Split path at basename.
    +   - ``os.path.splitdrive(p)``
        - ``p.splitdrive``

          or

          ``p.drivesplit``
        - ✔
        -
    +   - ``os.path.splitext(p)``
        - ``p.splitext``

          or

          ``p.extsplit``
        - ✔
        - Split at extension.
    +   - ``os.path.splitunc(p)``
        - ✖
        - ✖
        -
    +   - ``os.path.walk(p, func, args)``
        - ✖
        - ✖
        - It's deprecated in Python 3 anyway
    +   - ``os.readlink(p)``
        - ``p.readlink``
        - ✖
        - Return the path a symbolic link points to.
    +   - ``os.remove(p)``
        - ``p.remove()``
        - ?
        - Delete file.
    +   - ``os.removedirs(d)``
        - ``d.removedirs``
        - ?
        - Remove empty directory and all its empty ancestors.
    +   - ``os.rename(src, dst)``
        - ``p.rename(dst)``
        - ?
        - Rename a file or directory atomically (must be on same device).
    +   - ``os.renames(src, dst)``
        - ``p.renames(dst)``
        - ?
        - Combines os.rename, os.makedirs, and os.removedirs.
    +   - ``os.rmdir(d)``
        - ``d.rmdir()``
        - ?
        - Delete empty directory.
    +   - ``os.stat(p)``
        - ``p.stat()``
        - ?
        - Return a "stat" object.
    +   - ``os.statvfs(p)``
        - ``p.statvfs``
        - ?
        - Return a "statvfs" object.
    +   - ``os.symlink(src, dst)``
        - ``p.symlink(dst)``
        - ?
        - Create a symbolic link. ("write_link" argument order is opposite from Python's!)
    +   - ``os.unlink(f)``
        - ``f.unlink()``
        - ?
        - Same as .remove().
    +   - ``os.walk(p)``
        - ``p.tree``
        - ✔
        - Recursively yield files and directories.
    +   - ``os.utime(p, times)``
        - ``p.utime(times)``
        - ?
        - Set access/modification times.
    +   - ``shutil.copyfile(src, dst)``
        - ``f.copy(dst)``
        - ?
        - Copy file.  Unipath method is more than copyfile but less than copy2.
    +   - ``shutil.copy(src, dst)``
        - ``f.copy(dst)``
        - ?
        - High-level copy a la Unix "cp".

Extras
======

A *temporary path*::

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
