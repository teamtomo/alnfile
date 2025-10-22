"""
Functions to convert AreTomo alignment data to IMOD XF transformation matrices.
"""

import numpy as np
import pandas as pd


def df_to_xf(df: pd.DataFrame, yx: bool = False) -> np.ndarray:
    """
    Convert alignment DataFrame to IMOD .xf transformation matrix format.
    
    Constructs 2D affine transformation matrices from AreTomo alignment parameters.
    Each tilt image gets a 2x3 transformation matrix encoding rotation and translation.
    
    Parameters
    ----------
    df : pd.DataFrame
        Global alignment data with columns: rot, tx, ty
    yx : bool, default False
        Matrix row ordering:
        - False: [[A11, A12, DX], [A21, A22, DY]] (xy convention)
        - True:  [[A21, A22, DY], [A11, A12, DX]] (yx convention)
        
    Returns
    -------
    np.ndarray
        Transformation matrices with shape (n_tilts, 2, 3)
        
    Notes
    -----
    IMOD .xf format uses 6 values per tilt image: A11 A12 A21 A22 DX DY
    
    The transformation matrix components are:
        θ = -ROT
        A11, A22 = cos(θ)
        A12 = -sin(θ)  
        A21 = sin(θ)
        DX = A11*(-TX) + A12*(-TY)
        DY = A21*(-TX) + A22*(-TY)
    
    where θ is the rotation angle (ROT in the df) and (TX, TY) are the shifts (TX, TY in the df).
    """
    n_tilts = len(df)
    xf = np.zeros((n_tilts, 2, 3), dtype=np.float64)
    theta_rad = -1 * np.deg2rad(df['rot'].values)
    cos_theta = np.cos(theta_rad)
    sin_theta = np.sin(theta_rad)
    
    # Rotation matrix components
    A11 = cos_theta
    A12 = -sin_theta
    A21 = sin_theta
    A22 = cos_theta
    
    # Translation components 
    neg_tx = -df['tx'].values
    neg_ty = -df['ty'].values
    DX = A11 * neg_tx + A12 * neg_ty
    DY = A21 * neg_tx + A22 * neg_ty
    
    # Fill transformation matrices
    if yx:
        # YX convention: 
        xf[:, 0, 0] = A22
        xf[:, 0, 1] = A21
        xf[:, 0, 2] = DY
        xf[:, 1, 0] = A12
        xf[:, 1, 1] = A11
        xf[:, 1, 2] = DX
    else:
        # XY convention 
        xf[:, 0, 0] = A11
        xf[:, 0, 1] = A12
        xf[:, 0, 2] = DX
        xf[:, 1, 0] = A21
        xf[:, 1, 1] = A22
        xf[:, 1, 2] = DY
    
    return xf
