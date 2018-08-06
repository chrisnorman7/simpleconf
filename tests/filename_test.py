"""Test filenames."""

import os.path
from io import StringIO
from simpleconf2.filename import Filename


def test_defaults():
    name = 'test.txt'
    f = Filename(name)
    assert f.name == name
    assert f.read_flags == 'r'
    assert f.write_flags == 'w'
    assert f.file_like is False
    assert f.exists() is False


def test_with_file():
    name = os.path.join('test', __file__)
    f = Filename(name)
    assert f.exists() is True
    with open(name, 'r') as fp:
        assert f.read() == fp.read()


def test_with_filelike():
    s = 'Test string.'
    o = StringIO(s)
    f = Filename(o, file_like=True)
    assert f.exists() is True
    assert f.read() == s
    assert f.read() == s
