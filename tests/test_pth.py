import os
import zipfile
from aspectlib.test import Story
from pytest import mark, raises

import pth


def test_basename():
    assert pth("/my/abs/path").name == "path"
    assert pth("/my/abs/path").basename == "path"
    assert pth("path").name == "path"
    assert pth("path").basename == "path"
    assert pth("rel/path").name == "path"
    assert pth("rel/path").basename == "path"


def test_basename_zip():
    assert pth.ZipPath("tests/test.zip").name == "test.zip"
    assert pth.ZipPath("tests/test.zip").basename == "test.zip"

    assert (pth.ZipPath("tests/test.zip") / 'a').name == "a"
    assert (pth.ZipPath("tests/test.zip") / 'a').basename == "a"

    assert (pth.ZipPath("tests/test.zip") / 'a' / 'b').name == "b"
    assert (pth.ZipPath("tests/test.zip") / 'a' / 'b').basename == "b"


def test_dirname():
    assert pth("/my/abs/path").dir == "/my/abs"
    assert pth("/my/abs/path").dirname == "/my/abs"
    assert pth("path").dir == ""
    assert pth("path").dirname == ""
    assert pth("rel/path").dir == "rel"
    assert pth("rel/path").dirname == "rel"


def test_dirname_zip():
    assert pth.ZipPath("tests/test.zip").dir == "tests"
    assert pth.ZipPath("tests/test.zip").dirname == "tests"

    assert (pth.ZipPath("tests/test.zip") / "a").dir == "tests/test.zip"
    assert (pth.ZipPath("tests/test.zip") / "a").dirname == "tests/test.zip"

    assert (pth.ZipPath("tests/test.zip") / "a" / "b").dir == "tests/test.zip/a"
    assert (pth.ZipPath("tests/test.zip") / "a" / "b").dirname == "tests/test.zip/a"


def test_exists():
    assert pth("/").exists
    assert not pth("bogus/doesn't/exist").exists


def test_lexists():
    assert pth("/").lexists
    assert not pth("bogus/doesn't/exist").lexists


def test_exists_zip():
    with pth.tmp() as tmp:
        zp = pth.Path('tests/test.zip').copy(tmp)
        with tmp.cd:
            assert (pth("test.zip") / "a.txt").exists
            assert not (pth("test.zip") / "crappo").exists

            assert (pth(zp) / "a.txt").exists
            assert not (pth(zp) / "crappo").exists


def test_abspath():
    with pth.tmp().cd as tmp:
        assert pth("path").abs == tmp / "path"
        assert pth("path").abspath == tmp / "path"


def test_abspath_zip():
    with pth.tmp() as tmp:
        pth.Path('tests/test.zip').copy(tmp)
        with tmp.cd:
            assert pth("test.zip").abs == tmp / "test.zip"
            assert pth("test.zip").abspath == tmp / "test.zip"
            assert (pth("test.zip") / "a.txt").abs == tmp / "test.zip" / "a.txt"
            assert (pth("test.zip") / "a.txt").abspath == tmp / "test.zip" / "a.txt"


def test_repr():
    assert repr(pth('/bogus')) == "pth.Path('/bogus')"


def test_cd():
    assert repr(pth('/bogus').cd) == "pth.WorkingDir('/bogus')"

    with Story(['zipfile.is_zipfile', 'os.chdir', 'os.getcwd', 'os.path.exists', 'os.stat']) as story:
        zipfile.is_zipfile('/bogus') == False  # returns
        os.stat(pth.WorkingDir('/bogus')) == os.stat_result((17407, 2621441, 2049, 43, 0, 0, 3805184, 1406286835, 1408573505, 1408573505))  # returns
        os.getcwd() == '/current'  # returns
        os.chdir(pth.WorkingDir('/bogus')) == None  # returns

    with story.replay():
        pth('/bogus').cd()


def test_cd_context():
    with Story(['zipfile.is_zipfile', 'os.chdir', 'os.getcwd', 'os.path.exists', 'os.stat']) as story:
        zipfile.is_zipfile('/bogus') == False  # returns
        os.stat(pth.WorkingDir('/bogus')) == os.stat_result((17407, 2621441, 2049, 43, 0, 0, 3805184, 1406286835, 1408573505, 1408573505))  # returns
        os.getcwd() == '/current'  # returns
        os.chdir(pth.WorkingDir('/bogus')) == None  # returns
        os.chdir(pth.Path('/current')) == None  # returns

    with story.replay():
        with pth('/bogus').cd():
            pass

    with story.replay():
        with pth('/bogus').cd:
            pass


def test_expanduser():
    assert pth('~root').expanduser == os.path.expanduser('~root')
    assert pth('~/stuff').expanduser == os.path.expanduser('~/stuff')


def test_expandvars():
    os.environ['FOOBAR'] = "1"
    assert pth('$FOOBAR/stuff').expandvars == os.path.join("1", "stuff")


def test_zip_constructor():
    assert isinstance(pth.zip('tests/test.zip', None, 'a.txt'), pth.ZipPath)
    assert pth.zip('tests/test.zip', None, 'a.txt')('r').read() == b"A"


def test_zip_autocast():
    assert isinstance(pth('tests/test.zip'), pth.ZipPath)
    assert isinstance(pth('tests/test.zip')/'a', pth.ZipPath)
    assert isinstance(pth('tests/test.zip')/'a/b', pth.ZipPath)
    assert isinstance(pth('tests')/'test.zip', pth.ZipPath)
    assert isinstance(pth('tests')/pth('test.zip'), pth.ZipPath)


def test_expanduser_zip():
    assert pth('tests/test.zip/~root').expanduser == 'tests/test.zip/~root'


def test_expandvars():
    os.environ['FOOBAR'] = "1"
    assert pth('tests/test.zip/$FOOBAR').expandvars == os.path.join('tests', 'test.zip', '1')

    os.environ['FOOBAR'] = "test"
    assert isinstance(pth('tests/$FOOBAR.zip').expandvars, pth.ZipPath)


def test_time():
    assert isinstance(pth().atime, float)
    assert isinstance(pth().ctime, float)
    assert isinstance(pth().mtime, float)


def test_time_zip():
    assert isinstance(pth('tests/test.zip').atime, float)
    assert isinstance(pth('tests/test.zip').ctime, float)
    assert isinstance(pth('tests/test.zip').mtime, float)

    a = pth('tests/test.zip') / 'a.txt'

    assert raises(NotImplementedError, lambda: a.atime)
    assert isinstance(a.ctime, float)
    assert raises(NotImplementedError, lambda: a.mtime)


def test_size():
    assert isinstance(pth().size, int)
    assert pth('tests/b.txt').size == 1


def test_size_zip():
    assert (pth('tests/test.zip') / 'a.txt').size == 1
    assert (pth('tests/test.zip') / '1').isdir
    raises(pth.PathDoesNotExist, lambda: (pth('tests/test.zip') / '1').size)  # yeeeep, can't differentiate isdir from non-existing

