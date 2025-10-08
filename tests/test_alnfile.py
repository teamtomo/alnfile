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



