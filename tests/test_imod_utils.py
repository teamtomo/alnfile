"""
Simple tests to double check teh basic of  IMOD utility functions (df_to_xf, save_xf, save_tlt).
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import alnfile
from alnfile.imod_utils import df_to_xf, save_xf, save_tlt


class TestDfToXf:
    """Test class for df_to_xf function."""
    
    @pytest.fixture
    def simple_df(self):
        """Create a simple test DataFrame."""
        return pd.DataFrame({
            'sec': [0, 1, 2],
            'rot': [0.0, 45.0, -45.0],
            'gmag': [1.0, 1.0, 1.0],
            'tx': [0.0, 10.0, -5.0],
            'ty': [0.0, 5.0, 10.0],
            'smean': [1.0, 1.0, 1.0],
            'sfit': [1.0, 1.0, 1.0],
            'scale': [1.0, 1.0, 1.0],
            'base': [0.0, 0.0, 0.0],
            'tilt': [0.0, 30.0, -30.0]
        })
    
    def test_output_shape(self, simple_df):
        """Test that output has correct shape."""
        xf = df_to_xf(simple_df)
        assert xf.shape == (3, 2, 3)  # 3 tilts, 2x3 transformation matrices
    
    def test_output_dtype(self, simple_df):
        """Test that output has correct dtype."""
        xf = df_to_xf(simple_df)
        assert xf.dtype == np.float64
    
    def test_zero_rotation(self, simple_df):
        """Test transformation matrix for zero rotation."""
        # Only use first row (rot=0, tx=0, ty=0)
        df = simple_df.iloc[[0]]
        xf = df_to_xf(df, yx=False)
        
        # For zero rotation and zero translation:
        # A11=1, A12=0, A21=0, A22=1, DX=0, DY=0
        expected = np.array([[[1.0, 0.0, 0.0],
                              [0.0, 1.0, 0.0]]])
        
        np.testing.assert_array_almost_equal(xf, expected, decimal=6)
    
    def test_45_degree_rotation(self, simple_df):
        """Test transformation matrix for 45 degree rotation."""
        # Use second row (rot=45)
        df = simple_df.iloc[[1]]
        xf = df_to_xf(df, yx=False)
        
        # For 45 degree rotation:
        # A11 = A22 = cos(45°) ≈ 0.707107
        # A12 = -sin(45°) ≈ -0.707107
        # A21 = sin(45°) ≈ 0.707107
        sqrt2_inv = 1.0 / np.sqrt(2.0)
        
        # Check rotation components
        assert abs(xf[0, 0, 0] - sqrt2_inv) < 1e-6  # A11
        assert abs(xf[0, 0, 1] - (-sqrt2_inv)) < 1e-6  # A12
        assert abs(xf[0, 1, 0] - sqrt2_inv) < 1e-6  # A21
        assert abs(xf[0, 1, 1] - sqrt2_inv) < 1e-6  # A22
    
    def test_translation_calculation(self, simple_df):
        """Test that translations are calculated correctly."""
        # Use second row (rot=45, tx=10, ty=5)
        df = simple_df.iloc[[1]]
        xf = df_to_xf(df, yx=False)
        
        # DX = cos(45°)*(-10) + (-sin(45°))*(-5)
        # DY = sin(45°)*(-10) + cos(45°)*(-5)
        sqrt2_inv = 1.0 / np.sqrt(2.0)
        expected_dx = sqrt2_inv * (-10) + (-sqrt2_inv) * (-5)
        expected_dy = sqrt2_inv * (-10) + sqrt2_inv * (-5)
        
        assert abs(xf[0, 0, 2] - expected_dx) < 1e-6  # DX
        assert abs(xf[0, 1, 2] - expected_dy) < 1e-6  # DY
    

class TestSaveXf:
    """Test class for save_xf function."""
    
    @pytest.fixture
    def test_data_dir(self):
        """Return the test data directory."""
        return Path(__file__).parent
    
    @pytest.fixture
    def file_with_local(self, test_data_dir):
        """Return path to test file with local alignment."""
        return test_data_dir / "test_data_with_local.aln"
    
    @pytest.fixture
    def temp_xf_file(self, tmp_path):
        """Return path for temporary xf file."""
        return tmp_path / "test.xf"
    
    def test_save_xf_creates_file(self, file_with_local, temp_xf_file):
        """Test that save_xf creates a file."""
        save_xf(file_with_local, temp_xf_file)
        assert temp_xf_file.exists()
    
    def test_save_xf_file_format(self, file_with_local, temp_xf_file):
        """Test that saved xf file has correct format."""
        save_xf(file_with_local, temp_xf_file)
        
        # Read the file
        with open(temp_xf_file, 'r') as f:
            lines = f.readlines()
        
        # Should have lines
        assert len(lines) > 0
        
        # Each line should have 6 floating point numbers
        for line in lines:
            parts = line.strip().split()
            assert len(parts) == 6
            
            # All should be valid floats
            for part in parts:
                float(part)  # Should not raise
    

class TestSaveTlt:
    """Test class for save_tlt function."""
    
    @pytest.fixture
    def test_data_dir(self):
        """Return the test data directory."""
        return Path(__file__).parent
    
    @pytest.fixture
    def file_with_local(self, test_data_dir):
        """Return path to test file with local alignment."""
        return test_data_dir / "test_data_with_local.aln"
    
    @pytest.fixture
    def temp_tlt_file(self, tmp_path):
        """Return path for temporary tlt file."""
        return tmp_path / "test.tlt"
    
    def test_save_tlt_creates_file(self, file_with_local, temp_tlt_file):
        """Test that save_tlt creates a file."""
        save_tlt(file_with_local, temp_tlt_file)
        assert temp_tlt_file.exists()
    
    def test_save_tlt_file_format(self, file_with_local, temp_tlt_file):
        """Test that saved tlt file has correct format."""
        save_tlt(file_with_local, temp_tlt_file)
        
        # Read the file
        with open(temp_tlt_file, 'r') as f:
            lines = f.readlines()
        
        # Should have lines
        assert len(lines) > 0
        
        # Each line should have one floating point number
        for line in lines:
            parts = line.strip().split()
            assert len(parts) == 1
            
            # Should be a valid float
            angle = float(parts[0])
            
            # Tilt angles should be in reasonable range
            assert -90 <= angle <= 90
    
    def test_save_tlt_matches_alignment(self, file_with_local, temp_tlt_file):
        """Test that tlt file matches alignment data."""
        # Save tlt file
        save_tlt(file_with_local, temp_tlt_file)
        
        # Read alignment data
        df = alnfile.read(file_with_local, alignment_type="global")
        
        # Read tlt file
        with open(temp_tlt_file, 'r') as f:
            tlt_angles = [float(line.strip()) for line in f]
        
        # Should have same number of tilts
        assert len(tlt_angles) == len(df)
        
        # Angles should match
        for i, (tlt_angle, df_angle) in enumerate(zip(tlt_angles, df['tilt'].values)):
            assert abs(tlt_angle - df_angle) < 0.01, f"Mismatch at index {i}"


class TestNumpyOutput:
    """Test numpy output format for read function."""
    
    @pytest.fixture
    def test_data_dir(self):
        """Return the test data directory."""
        return Path(__file__).parent
    
    @pytest.fixture
    def file_with_local(self, test_data_dir):
        """Return path to test file with local alignment."""
        return test_data_dir / "test_data_with_local.aln"
    
    def test_read_global_numpy(self, file_with_local):
        """Test reading global alignments as numpy array."""
        arr = alnfile.read(file_with_local, alignment_type="global", output_format="numpy")
        
        assert isinstance(arr, np.ndarray)
        assert arr.ndim == 2
        assert arr.shape[1] == 10  # 10 columns
        assert arr.dtype == np.float64
    
    def test_read_local_numpy(self, file_with_local):
        """Test reading local alignments as numpy array."""
        arr = alnfile.read(file_with_local, alignment_type="local", output_format="numpy")
        
        assert isinstance(arr, np.ndarray)
        assert arr.ndim == 2
        assert arr.shape[1] == 7  # 7 columns
        assert arr.dtype == np.float64
    
    def test_numpy_vs_pandas_values(self, file_with_local):
        """Test that numpy and pandas outputs have same values."""
        df = alnfile.read(file_with_local, alignment_type="global", output_format="pandas")
        arr = alnfile.read(file_with_local, alignment_type="global", output_format="numpy")
        
        # Values should be identical
        np.testing.assert_array_almost_equal(df.values, arr)
    
    def test_both_with_numpy_raises(self, file_with_local):
        """Test that alignment_type='both' with numpy raises error."""
        with pytest.raises(ValueError, match="output_format='numpy' is not supported for alignment_type='both'"):
            alnfile.read(file_with_local, alignment_type="both", output_format="numpy")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

