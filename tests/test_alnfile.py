import pytest
from pathlib import Path
import pandas as pd

import alnfile


def test_imports_with_version():
    """Test that alnfile can be imported and has a version."""
    assert isinstance(alnfile.__version__, str)


def test_read_function_available():
    """Test that the read function is available."""
    assert hasattr(alnfile, 'read')
    assert callable(alnfile.read)


def test_import():
    """Test that alnfile can be imported and has the read function."""
    assert hasattr(alnfile, 'read')
    assert callable(alnfile.read)


@pytest.mark.parametrize("file_fixture", ["file_with_local", "file_no_local"])
def test_read_global_alignments(file_fixture, request):
    """Test reading only global alignments from both file types."""
    file = request.getfixturevalue(file_fixture)
    df = alnfile.read(file, alignment_type="global")

    # Check basic structure
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

    # Check columns
    expected_cols = ['sec', 'rot', 'gmag', 'tx', 'ty', 'smean', 'sfit', 'scale', 'base', 'tilt']
    assert list(df.columns) == expected_cols

    # Check data types
    assert df['sec'].dtype == 'int64'
    for col in ['rot', 'gmag', 'tx', 'ty', 'smean', 'sfit', 'scale', 'base', 'tilt']:
        assert pd.api.types.is_numeric_dtype(df[col])


def test_read_local_alignments(file_with_local):
    """Test reading only local alignments from file with local alignment."""
    df = alnfile.read(file_with_local, alignment_type="local")

    # Check basic structure
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

    # Check columns
    expected_cols = ['sec_idx', 'patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']
    assert list(df.columns) == expected_cols

    # Check data types
    assert df['sec_idx'].dtype == 'int64'
    assert df['patch_idx'].dtype == 'int64'
    for col in ['center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']:
        assert pd.api.types.is_numeric_dtype(df[col])


def test_read_local_raises_if_not_present(file_no_local):
    with pytest.raises(ValueError, match="Local alignment has not been performed"):
        alnfile.read(file_no_local, alignment_type="local")


def test_read_default_behavior(file_with_local):
    """Test that default behavior is 'global'."""
    df_default = alnfile.read(file_with_local)
    df_both = alnfile.read(file_with_local, alignment_type="global")

    pd.testing.assert_frame_equal(df_default, df_both)


def test_invalid_alignment_type(file_with_local):
    """Test that invalid alignment_type raises ValueError."""
    with pytest.raises(ValueError, match="alignment_type must be one of"):
        alnfile.read(file_with_local, alignment_type="invalid")


def test_nonexistent_file():
    """Test that nonexistent file raises ValueError."""
    with pytest.raises(ValueError, match="File does not exist"):
        alnfile.read(Path("nonexistent_file.aln"))


def test_directory_instead_of_file(data_dir):
    """Test that passing a directory raises ValueError."""
    with pytest.raises(ValueError, match="Path is not a file"):
        alnfile.read(data_dir)
