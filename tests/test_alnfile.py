import alnfile


def test_imports_with_version():
    assert isinstance(alnfile.__version__, str)
