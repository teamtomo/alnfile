
"""
Comprehensive tests for the alnfile reader module.
"""

import pytest
import warnings
from pathlib import Path
import pandas as pd
import sys

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import alnfile
from alnfile.reader import AreTomo3ALN, GlobalAlignmentInfo, LocalAlignmentInfo


class TestAlnfileReader:
    """Test class for alnfile reader functionality."""
    
    @pytest.fixture
    def test_data_dir(self):
        """Return the test data directory."""
        return Path(__file__).parent
    
    @pytest.fixture
    def file_with_local(self, test_data_dir):
        """Return path to test file with local alignment."""
        return test_data_dir / "test_data_with_local.aln"
    
    @pytest.fixture
    def file_no_local(self, test_data_dir):
        """Return path to test file without local alignment."""
        return test_data_dir / "test_data_no_local.aln"
    
    def test_import(self):
        """Test that alnfile can be imported and has the read function."""
        assert hasattr(alnfile, 'read')
        assert callable(alnfile.read)
    
    def test_read_global_only_with_local_file(self, file_with_local):
        """Test reading only global alignments from file with local alignment."""
        df = alnfile.read(file_with_local, alignment_type="global")
        
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
    
    def test_read_global_only_no_local_file(self, file_no_local):
        """Test reading only global alignments from file without local alignment."""
        df = alnfile.read(file_no_local, alignment_type="global")
        
        # Check basic structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        
        # Check columns
        expected_cols = ['sec', 'rot', 'gmag', 'tx', 'ty', 'smean', 'sfit', 'scale', 'base', 'tilt']
        assert list(df.columns) == expected_cols
    
    def test_read_local_only_with_local_file(self, file_with_local):
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
    
    def test_read_local_only_no_local_file(self, file_no_local):
        """Test reading only local alignments from file without local alignment."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            df = alnfile.read(file_no_local, alignment_type="local")
            
            # Check that warning was raised
            assert len(w) == 1
            assert "Probably local alignment has not been performed" in str(w[0].message)
        
        # Check that empty DataFrame with correct columns is returned
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        expected_cols = ['sec_idx', 'patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']
        assert list(df.columns) == expected_cols
    
    def test_read_both_with_local_file(self, file_with_local):
        """Test reading both alignments from file with local alignment."""
        df = alnfile.read(file_with_local, alignment_type="both")
        
        # Check basic structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        
        # Check that we have both types
        assert 'type' in df.columns
        types = df['type'].unique()
        assert 'global' in types
        assert 'local' in types
        
        # Check that global and local rows have appropriate data
        global_rows = df[df['type'] == 'global']
        local_rows = df[df['type'] == 'local']
        
        assert len(global_rows) > 0
        assert len(local_rows) > 0
        
        # Global rows should have global data and None for local columns
        assert global_rows['rot'].notna().all()
        assert global_rows['patch_idx'].isna().all()
        
        # Local rows should have local data and None for global columns
        assert local_rows['patch_idx'].notna().all()
        assert local_rows['rot'].isna().all()
    
    def test_read_both_no_local_file(self, file_no_local):
        """Test reading both alignments from file without local alignment."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            df = alnfile.read(file_no_local, alignment_type="both")
            
            # Check that warning was raised
            assert len(w) == 1
            assert "Probably local alignment has not been performed" in str(w[0].message)
        
        # Check basic structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        
        # Check that we only have global type
        assert 'type' in df.columns
        types = df['type'].unique()
        assert 'global' in types
        assert 'local' not in types
        
        # Check that all local columns are None
        for col in ['patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']:
            assert df[col].isna().all()
    
    def test_read_default_behavior(self, file_with_local):
        """Test that default behavior is 'both'."""
        df_default = alnfile.read(file_with_local)
        df_both = alnfile.read(file_with_local, alignment_type="both")
        
        pd.testing.assert_frame_equal(df_default, df_both)
    
    def test_invalid_alignment_type(self, file_with_local):
        """Test that invalid alignment_type raises ValueError."""
        with pytest.raises(ValueError, match="alignment_type must be one of"):
            alnfile.read(file_with_local, alignment_type="invalid")
    
    def test_nonexistent_file(self):
        """Test that nonexistent file raises ValueError."""
        with pytest.raises(ValueError, match="File does not exist"):
            alnfile.read(Path("nonexistent_file.aln"))
    
    def test_directory_instead_of_file(self, test_data_dir):
        """Test that passing a directory raises ValueError."""
        with pytest.raises(ValueError, match="Path is not a file"):
            alnfile.read(test_data_dir)


class TestAreTomo3ALN:
    """Test class for AreTomo3ALN class."""
    
    @pytest.fixture
    def test_data_dir(self):
        """Return the test data directory."""
        return Path(__file__).parent
    
    @pytest.fixture
    def file_with_local(self, test_data_dir):
        """Return path to test file with local alignment."""
        return test_data_dir / "test_data_with_local.aln"
    
    @pytest.fixture
    def file_no_local(self, test_data_dir):
        """Return path to test file without local alignment."""
        return test_data_dir / "test_data_no_local.aln"
    
    def test_from_file_with_local(self, file_with_local):
        """Test loading AreTomo3ALN from file with local alignment."""
        aln = AreTomo3ALN.from_file(file_with_local)
        
        assert isinstance(aln, AreTomo3ALN)
        assert aln.NumPatches > 0
        assert len(aln.GlobalAlignments) > 0
        assert len(aln.LocalAlignments) > 0
        assert len(aln.DarkFrames) > 0  # This file has dark frames
    
    def test_from_file_no_local(self, file_no_local):
        """Test loading AreTomo3ALN from file without local alignment."""
        aln = AreTomo3ALN.from_file(file_no_local)
        
        assert isinstance(aln, AreTomo3ALN)
        assert aln.NumPatches == 0
        assert len(aln.GlobalAlignments) > 0
        assert len(aln.LocalAlignments) == 0
        assert len(aln.DarkFrames) == 0  # This file has no dark frames
    
    def test_get_global_alignments(self, file_with_local):
        """Test getting global alignments as DataFrame."""
        aln = AreTomo3ALN.from_file(file_with_local)
        df = aln.get_global_alignments()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        expected_cols = ['sec', 'rot', 'gmag', 'tx', 'ty', 'smean', 'sfit', 'scale', 'base', 'tilt']
        assert list(df.columns) == expected_cols
    
    def test_get_local_alignments_with_data(self, file_with_local):
        """Test getting local alignments as DataFrame when data exists."""
        aln = AreTomo3ALN.from_file(file_with_local)
        df = aln.get_local_alignments()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        expected_cols = ['sec_idx', 'patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']
        assert list(df.columns) == expected_cols
    
    def test_get_local_alignments_no_data(self, file_no_local):
        """Test getting local alignments as DataFrame when no data exists."""
        aln = AreTomo3ALN.from_file(file_no_local)
        df = aln.get_local_alignments()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        expected_cols = ['sec_idx', 'patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']
        assert list(df.columns) == expected_cols
    
    def test_pandas_method(self, file_with_local):
        """Test the pandas method that returns both DataFrames."""
        aln = AreTomo3ALN.from_file(file_with_local)
        global_df, local_df = aln.pandas()
        
        assert isinstance(global_df, pd.DataFrame)
        assert isinstance(local_df, pd.DataFrame)
        assert len(global_df) > 0
        assert len(local_df) > 0


class TestAlignmentInfoClasses:
    """Test class for alignment info classes."""
    
    def test_global_alignment_info_creation(self):
        """Test creating GlobalAlignmentInfo."""
        info = GlobalAlignmentInfo(sec=1, rot=0.5, tx=10.0, ty=20.0, tilt=-60.0)
        assert info.sec == 1
        assert info.rot == 0.5
        assert info.tx == 10.0
        assert info.ty == 20.0
        assert info.tilt == -60.0
        assert info.gmag == 1.0  # default value
    
    def test_global_alignment_info_from_string(self):
        """Test parsing GlobalAlignmentInfo from string."""
        line = "    1   -95.4040    1.00000      9.220    103.933     1.00     1.00     1.00     0.00    -63.20"
        info = GlobalAlignmentInfo.from_string(line)
        
        assert info.sec == 1
        assert abs(info.rot - (-95.4040)) < 1e-4
        assert abs(info.gmag - 1.00000) < 1e-5
        assert abs(info.tx - 9.220) < 1e-3
        assert abs(info.ty - 103.933) < 1e-3
        assert abs(info.tilt - (-63.20)) < 1e-2
    
    def test_local_alignment_info_creation(self):
        """Test creating LocalAlignmentInfo."""
        info = LocalAlignmentInfo(
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
    
    def test_local_alignment_info_from_string(self):
        """Test parsing LocalAlignmentInfo from string."""
        line = "   0   0 -1537.16  -1363.14     -6.93    -36.22   1.0"
        info = LocalAlignmentInfo.from_string(line)
        
        assert info.sec_idx == 0
        assert info.patch_idx == 0
        assert abs(info.center_x - (-1537.16)) < 1e-2
        assert abs(info.center_y - (-1363.14)) < 1e-2
        assert abs(info.shift_x - (-6.93)) < 1e-2
        assert abs(info.shift_y - (-36.22)) < 1e-2
        assert abs(info.is_reliable - 1.0) < 1e-1
    
    def test_global_alignment_field_names(self):
        """Test GlobalAlignmentInfo field names property."""
        info = GlobalAlignmentInfo(sec=0, rot=0.0, tx=0.0, ty=0.0, tilt=0.0)
        expected = ['sec', 'rot', 'gmag', 'tx', 'ty', 'smean', 'sfit', 'scale', 'base', 'tilt']
        assert info.field_names == expected
    
    def test_local_alignment_field_names(self):
        """Test LocalAlignmentInfo field names property."""
        info = LocalAlignmentInfo(sec_idx=0, patch_idx=0, center_x=0.0, center_y=0.0, 
                                 shift_x=0.0, shift_y=0.0, is_reliable=1.0)
        expected = ['sec_idx', 'patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']
        assert info.field_names == expected


if __name__ == "__main__":
    pytest.main([__file__])
