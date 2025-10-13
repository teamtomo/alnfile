# alnfile

[![License](https://img.shields.io/pypi/l/alnfile.svg?color=green)](https://github.com/teamtomo/alnfile/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/alnfile.svg?color=green)](https://pypi.org/project/alnfile)
[![Python Version](https://img.shields.io/pypi/pyversions/alnfile.svg?color=green)](https://python.org)
[![CI](https://github.com/teamtomo/alnfile/actions/workflows/ci.yml/badge.svg)](https://github.com/teamtomo/alnfile/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/teamtomo/alnfile/branch/main/graph/badge.svg)](https://codecov.io/gh/teamtomo/alnfile)

A Python package for reading AreTomo alignment files into pandas DataFrames, with utilities for
converting to IMOD transformation matrices.

## Installation

```bash
pip install alnfile
```

## Quick start

### Basic usage 

The main function is `alnfile.read()` which accepts a file path and an optional alignment type:

```python
import alnfile

# Read either global or local alignments (default global)
global_df = alnfile.read("path/to/your/file.aln")
print(global_df.head())
# Columns: sec, rot, gmag, tx, ty, smean, sfit, scale, base, tilt

# Local alignments   
local_df = alnfile.read("file.aln", alignment_type="local")
print(local_df.head())
# Columns: sec_idx, patch_idx, center_x, center_y, shift_x, shift_y, is_reliable


```

### IMOD Transformation Matrices

Convert alignment data to IMOD-compatible transformation matrices:

```python
import alnfile

# Read alignment data
df = alnfile.read("path/to/your/file.aln")

# Convert DataFrame to transformation matrices (IMOD .xf format)
xf_matrices = alnfile.df_to_xf(df)  # Returns (n_tilts, 2, 3) array
# Each matrix is [[A11, A12, DX], [A21, A22, DY]]

# Use yx convention (swap rows) if needed for specific applications
xf_matrices_yx = alnfile.df_to_xf(df, yx=True)  # Returns (n_tilts, 2, 3) array
# Each matrix is [[A22, A21, DY], [A12, A11, DX]]
```

## Data Structure

#### Global Alignment DataFrame

| Column | Type  | Description                                                             |
|--------|-------|-------------------------------------------------------------------------|
| sec    | int   | Zero-indexed position in the final aligned stack (excludes dark frames) |
| rot    | float | Rotation angle of the tilt axis relative to Y-axis (degrees)            |
| gmag   | float | Global magnification adjustment factor                                  |
| tx     | float | X shift (pixels)                                                        |
| ty     | float | Y shift (pixels)                                                        |
| smean  | float | Statistical metric (implementation-specific, see AreTomo docs)          |
| sfit   | float | Statistical metric (implementation-specific, see AreTomo docs)          |
| scale  | float | Scaling parameter for this tilt                                         |
| base   | float | Implementation-specific parameter (see AreTomo docs)                    |
| tilt   | float | Nominal tilt angle (degrees)                                            |

#### Local Alignment DataFrame

| Column      | Type  | Description                                                                      |
|-------------|-------|----------------------------------------------------------------------------------|
| sec_idx     | int   | Tilt position in final tilt series stack, zero-indexed (post dark frame removal) |
| patch_idx   | int   | Sequential patch identifier within this tilt image (zero-indexed)                |
| center_x    | float | Expected x position of patch center relative to image center (pixels)            |
| center_y    | float | Expected y position of patch center relative to image center (pixels)            |
| shift_x     | float | Measured x deviation from expected patch position (pixels)                       |
| shift_y     | float | Measured y deviation from expected patch position (pixels)                       |
| is_reliable | float | Confidence flag for patch alignment quality (1.0=reliable, 0.0=unreliable)       |


Rows will have `None` values for columns not applicable to their type.

## Attribution

This implementation has been adapted from a similar reader
in [cryoet-alignment repository](https://github.com/uermel/cryoet-alignment/blob/main/src/cryoet_alignment/io/aretomo3/aln.py)
by **Utz H. Ermel** (@uermel).