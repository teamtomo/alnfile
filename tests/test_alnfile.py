"""
Basic import and version tests for alnfile.
"""

import alnfile


def test_imports_with_version():
    """Test that alnfile can be imported and has a version."""
    assert isinstance(alnfile.__version__, str)


def test_read_function_available():
    """Test that the read function is available."""
    assert hasattr(alnfile, 'read')
    assert callable(alnfile.read)


def test_attribution_in_docstring():
    """Test that attribution is present in the package docstring."""
    assert "cryoet-alignment" in alnfile.__doc__
    assert "uermel" in alnfile.__doc__
