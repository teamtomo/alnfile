"""
Utilities for converting AreTomo alignment data to IMOD file formats.

Provides functions to export alignment data as.xf and .tlt files.
"""

from pathlib import Path
import numpy as np
import pandas as pd

from .reader import AreTomo3ALN


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
        A11, A22 = cos(θ)
        A12 = -sin(θ)  
        A21 = sin(θ)
        DX = A11*(-TX) + A12*(-TY)
        DY = A21*(-TX) + A22*(-TY)
    
    where θ is the rotation angle (ROT in the df) and (TX, TY) are the shifts (TX, TY in the df).
    """
    n_tilts = len(df)
    xf = np.zeros((n_tilts, 2, 3), dtype=np.float64)
    
    theta_rad = np.deg2rad(df['rot'].values)
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
        xf[:, 0, 0] = A21
        xf[:, 0, 1] = A22
        xf[:, 0, 2] = DY
        xf[:, 1, 0] = A11
        xf[:, 1, 1] = A12
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


def save_xf(
    file: Path | str,
    output_file: Path | str,
    include_dark: bool = False,
    yx: bool = False
) -> None:
    """
    Export alignment data to IMOD .xf transformation file.
    
    Parameters
    ----------
    file : Path | str
        Input AreTomo .aln file path
    output_file : Path | str
        Output .xf file path
    include_dark : bool, default False
        If True, include dark frames with identity transformations (all zeros).
        This creates an .xf file matching the original tilt series size.
    yx : bool, default False
        Matrix row ordering (see df_to_xf for details)
        
    Notes
    -----
    Writes one line per tilt image in format: A11 A12 A21 A22 DX DY
    Dark frames (when included) get identity transformation: 1 0 0 1 0 0
    """
    # Load alignment data
    aln_data = AreTomo3ALN.from_file(Path(file))
    global_df = aln_data.get_global_alignments(kind="pandas")
    
    # Convert to transformation matrices
    xf_matrices = df_to_xf(global_df, yx=yx)
    
    # Prepare output data
    if include_dark and aln_data.DarkFrames:
        # Create a complete list with dark frames as identity transformations
        # Dark frames have section_idx in original series, GlobalAlignments have sec after removal
        dark_indices = sorted([df.section_idx for df in aln_data.DarkFrames])
        
        # Build complete transformation list
        all_xf = []
        global_idx = 0
        

        total_images = aln_data.RawSize[2] if aln_data.RawSize else (len(xf_matrices) + len(dark_indices))
        
        for orig_idx in range(total_images):
            if orig_idx in dark_indices:
                # Identity transformation for dark frame
                all_xf.append(np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]))
            else:
                # Use alignment data
                if global_idx < len(xf_matrices):
                    all_xf.append(xf_matrices[global_idx])
                    global_idx += 1
        
        xf_matrices = all_xf
    
    # Write to file
    output_path = Path(output_file)
    with open(output_path, 'w') as f:
        for matrix in xf_matrices:
            # Flatten to 6 values: A11 A12 A21 A22 DX DY
            if yx:
                # Need to reorder back to standard XF format
                A21, A22, DY = matrix[0]
                A11, A12, DX = matrix[1]
            else:
                A11, A12, DX = matrix[0]
                A21, A22, DY = matrix[1]
            
            f.write(f"{A11:11.7f} {A12:11.7f} {A21:11.7f} {A22:11.7f} {DX:11.4f} {DY:11.4f}\n")


def save_tlt(
    file: Path | str,
    output_file: Path | str,
    include_dark: bool = False
) -> None:
    """
    Export tilt angles to IMOD .tlt file.
    
    Parameters
    ----------
    file : Path | str
        Input AreTomo .aln file path
    output_file : Path | str
        Output .tlt file path
    include_dark : bool, default False
        If True, include dark frames with their original tilt angles.
        This creates a .tlt file matching the original tilt series size.
        
    Notes
    -----
    Writes one tilt angle per line in degrees.
    """
    # Load alignment data
    aln_data = AreTomo3ALN.from_file(Path(file))
    global_df = aln_data.get_global_alignments(kind="pandas")
    
    # Prepare tilt angles
    if include_dark and aln_data.DarkFrames:
        # Create complete list including dark frame angles
        dark_frames = sorted(aln_data.DarkFrames, key=lambda x: x.section_idx)
        dark_dict = {df.section_idx: df.angle for df in dark_frames}
        
        # Build complete angle list
        all_tilts = []
        global_idx = 0
        
        total_images = aln_data.RawSize[2] if aln_data.RawSize else (len(global_df) + len(dark_frames))
        
        for orig_idx in range(total_images):
            if orig_idx in dark_dict:
                # Use dark frame angle
                all_tilts.append(dark_dict[orig_idx])
            else:
                # Use alignment data
                if global_idx < len(global_df):
                    all_tilts.append(global_df.iloc[global_idx]['tilt'])
                    global_idx += 1
        
        tilt_angles = all_tilts
    else:
        tilt_angles = global_df['tilt'].values
    
    # Write tilt angles
    output_path = Path(output_file)
    with open(output_path, 'w') as f:
        for tilt_angle in tilt_angles:
            f.write(f"{tilt_angle:8.2f}\n")

