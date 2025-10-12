import pytest
import pandas as pd

from alnfile.data_model import (
    AlnData,
    PatchAlignmentParameters,
    TiltImageAlignmentParameters,
)
from alnfile.df_utils import (
    global_alignments_to_dataframe,
    local_alignments_to_dataframe,
)


def test_from_file_with_local(file_with_local):
    """Test loading AlnFile from file with local alignment."""
    aln = AlnData.from_file(file_with_local)

    assert isinstance(aln, AlnData)
    assert aln.NumPatches > 0
    assert len(aln.GlobalAlignments) > 0
    assert len(aln.LocalAlignments) > 0
    assert len(aln.DarkFrames) > 0  # This file has dark frames


def test_from_file_no_local(file_no_local):
    """Test loading AlnFile from file without local alignment."""
    aln = AlnData.from_file(file_no_local)

    assert isinstance(aln, AlnData)
    assert aln.NumPatches == 0
    assert len(aln.GlobalAlignments) > 0
    assert len(aln.LocalAlignments) == 0
    assert len(aln.DarkFrames) == 0  # This file has no dark frames


def test_get_global_alignments(file_with_local):
    """Test getting global alignments as DataFrame."""
    aln = AlnData.from_file(file_with_local)
    df = global_alignments_to_dataframe(aln.GlobalAlignments)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    expected_cols = ['sec', 'rot', 'gmag', 'tx', 'ty', 'smean', 'sfit', 'scale', 'base', 'tilt']
    assert list(df.columns) == expected_cols


def test_get_local_alignments_with_data(file_with_local):
    """Test getting local alignments as DataFrame when data exists."""
    aln = AlnData.from_file(file_with_local)
    df = local_alignments_to_dataframe(aln.LocalAlignments)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    expected_cols = ['sec_idx', 'patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']
    assert list(df.columns) == expected_cols


def test_get_local_alignments_no_data(file_no_local):
    """Test getting local alignments as DataFrame when no data exists."""
    aln = AlnData.from_file(file_no_local)
    df = local_alignments_to_dataframe(aln.LocalAlignments)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    expected_cols = ['sec_idx', 'patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']
    assert list(df.columns) == expected_cols


def test_global_alignment_info_creation():
    """Test creating GlobalAlignmentParameters."""
    info = TiltImageAlignmentParameters(sec=1, rot=0.5, tx=10.0, ty=20.0, tilt=-60.0)
    assert info.sec == 1
    assert info.rot == 0.5
    assert info.tx == 10.0
    assert info.ty == 20.0
    assert info.tilt == -60.0
    assert info.gmag == 1.0  # default value


def test_global_alignment_info_from_string():
    """Test parsing GlobalAlignmentParameters from string."""
    line = "    1   -95.4040    1.00000      9.220    103.933     1.00     1.00     1.00     0.00    -63.20"
    info = TiltImageAlignmentParameters.from_string(line)

    assert info.sec == 1
    assert abs(info.rot - (-95.4040)) < 1e-4
    assert abs(info.gmag - 1.00000) < 1e-5
    assert abs(info.tx - 9.220) < 1e-3
    assert abs(info.ty - 103.933) < 1e-3
    assert abs(info.tilt - (-63.20)) < 1e-2


def test_local_alignment_info_creation():
    """Test creating LocalAlignmentParameters."""
    info = PatchAlignmentParameters(
        sec_idx=0, patch_idx=1, center_x=100.0, center_y=200.0,
        shift_x=1.5, shift_y=2.5, is_reliable=1.0
    )
    assert info.sec_idx == 0
    assert info.patch_idx == 1
    assert info.center_x == 100.0
    assert info.center_y == 200.0
    assert info.shift_x == 1.5
    assert info.shift_y == 2.5
    assert info.is_reliable == 1.0


def test_local_alignment_info_from_string():
    """Test parsing LocalAlignmentParameters from string."""
    line = "   0   0 -1537.16  -1363.14     -6.93    -36.22   1.0"
    info = PatchAlignmentParameters.from_string(line)

    assert info.sec_idx == 0
    assert info.patch_idx == 0
    assert abs(info.center_x - (-1537.16)) < 1e-2
    assert abs(info.center_y - (-1363.14)) < 1e-2
    assert abs(info.shift_x - (-6.93)) < 1e-2
    assert abs(info.shift_y - (-36.22)) < 1e-2
    assert abs(info.is_reliable - 1.0) < 1e-1


def test_global_alignment_field_names():
    """Test GlobalAlignmentParameters field names property."""
    info = TiltImageAlignmentParameters(sec=0, rot=0.0, tx=0.0, ty=0.0, tilt=0.0)
    expected = ['sec', 'rot', 'gmag', 'tx', 'ty', 'smean', 'sfit', 'scale', 'base', 'tilt']
    assert info.field_names == expected


def test_local_alignment_field_names():
    """Test LocalAlignmentParameters field names property."""
    info = PatchAlignmentParameters(sec_idx=0, patch_idx=0, center_x=0.0, center_y=0.0,
                                    shift_x=0.0, shift_y=0.0, is_reliable=1.0
                                    )
    expected = ['sec_idx', 'patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']
    assert info.field_names == expected
