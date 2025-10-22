import numpy as np

import alnfile


def test_output_shape(simple_df):
    """Test that output has correct shape."""
    xf = alnfile.df_to_xf(simple_df)
    assert xf.shape == (3, 2, 3)  # 3 tilts, 2x3 transformation matrices


def test_output_dtype(simple_df):
    """Test that output has correct dtype."""
    xf = alnfile.df_to_xf(simple_df)
    assert xf.dtype == np.float64


def test_zero_rotation(simple_df):
    """Test transformation matrix for zero rotation."""
    # Only use first row (rot=0, tx=0, ty=0)
    df = simple_df.iloc[[0]]
    xf = alnfile.df_to_xf(df, yx=False)

    # For zero rotation and zero translation:
    # A11=1, A12=0, A21=0, A22=1, DX=0, DY=0
    expected = np.array([[[1.0, 0.0, 0.0],
                          [0.0, 1.0, 0.0]]]
                        )

    np.testing.assert_array_almost_equal(xf, expected, decimal=6)


def test_45_degree_rotation(simple_df):
    """Test transformation matrix for 45 degree rotation."""
    # Use second row (rot=45)
    df = simple_df.iloc[[1]]
    xf = alnfile.df_to_xf(df, yx=False)

    # For rot=45 degree, θ = -45°:
    # A11 = A22 = cos(-45°) = cos(45°) ≈ 0.707107
    # A12 = -sin(-45°) = sin(45°) ≈ 0.707107
    # A21 = sin(-45°) = -sin(45°) ≈ -0.707107
    sqrt2_inv = 1.0 / np.sqrt(2.0)

    # Check rotation components
    assert abs(xf[0, 0, 0] - sqrt2_inv) < 1e-6  # A11
    assert abs(xf[0, 0, 1] - sqrt2_inv) < 1e-6  # A12
    assert abs(xf[0, 1, 0] - (-sqrt2_inv)) < 1e-6  # A21
    assert abs(xf[0, 1, 1] - sqrt2_inv) < 1e-6  # A22


def test_translation_calculation(simple_df):
    """Test that translations are calculated correctly."""
    # Use second row (rot=45, tx=10, ty=5)
    df = simple_df.iloc[[1]]
    xf = alnfile.df_to_xf(df, yx=False)

    # With θ = -45° (from rot=45):
    # DX = A11*(-10) + A12*(-5) = cos(-45°)*(-10) + (-sin(-45°))*(-5)
    # DY = A21*(-10) + A22*(-5) = sin(-45°)*(-10) + cos(-45°)*(-5)
    sqrt2_inv = 1.0 / np.sqrt(2.0)
    expected_dx = sqrt2_inv * (-10) + sqrt2_inv * (-5)
    expected_dy = (-sqrt2_inv) * (-10) + sqrt2_inv * (-5)

    assert abs(xf[0, 0, 2] - expected_dx) < 1e-6  # DX
    assert abs(xf[0, 1, 2] - expected_dy) < 1e-6  # DY
