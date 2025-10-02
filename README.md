# alnfile

[![License](https://img.shields.io/pypi/l/alnfile.svg?color=green)](https://github.com/teamtomo/alnfile/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/alnfile.svg?color=green)](https://pypi.org/project/alnfile)
[![Python Version](https://img.shields.io/pypi/pyversions/alnfile.svg?color=green)](https://python.org)
[![CI](https://github.com/teamtomo/alnfile/actions/workflows/ci.yml/badge.svg)](https://github.com/teamtomo/alnfile/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/teamtomo/alnfile/branch/main/graph/badge.svg)](https://codecov.io/gh/teamtomo/alnfile)

A Python package for reading AreTomo alignment files into pandas DataFrames.

## Requirements

- Python 3.10 or later
- pandas >= 1.5.0

## Installation

```bash
pip install alnfile
```

## Quick Start

```python
import alnfile
from pathlib import Path

# Read all alignment data (default behavior)
df = alnfile.read("your_file.aln")

# Read only global alignments
global_df = alnfile.read("your_file.aln", alignment_type="global")

# Read only local alignments
local_df = alnfile.read("your_file.aln", alignment_type="local")
```

## Usage

### Basic Usage

The main function is `alnfile.read()` which accepts a file path and an optional alignment type:

```python
import alnfile

# Read both global and local alignments (default)
df = alnfile.read("path/to/your/file.aln")
print(df.head())

# Global alignments only
global_df = alnfile.read("file.aln", alignment_type="global")
# Columns: sec, rot, gmag, tx, ty, smean, sfit, scale, base, tilt

# Local alignments only  
local_df = alnfile.read("file.aln", alignment_type="local")
# Columns: sec_idx, patch_idx, center_x, center_y, shift_x, shift_y, is_reliable

# Both alignments (default)
both_df = alnfile.read("file.aln", alignment_type="both")
# Combined DataFrame with 'type' column indicating 'global' or 'local'
```

### Data Structure

#### Global Alignment DataFrame
| Column | Type | Description |
|--------|------|-------------|
| sec | int | Section index (0-based, after dark frame removal) |
| rot | float | Tilt axis rotation angle (degrees) |
| gmag | float | Magnification change |
| tx | float | X translation (pixels) |
| ty | float | Y translation (pixels) |
| smean | float | TBD |
| sfit | float | TBD |
| scale | float | TBD |
| base | float | TBD |
| tilt | float | Tilt angle (degrees) |

#### Local Alignment DataFrame
| Column | Type | Description |
|--------|------|-------------|
| sec_idx | int | Section index (0-based, after dark frame removal) |
| patch_idx | int | Patch index (0-based) |
| center_x | float | Projected X coordinate of patch center |
| center_y | float | Projected Y coordinate of patch center |
| shift_x | float | X shift from expected patch center |
| shift_y | float | Y shift from expected patch center |
| is_reliable | float | Reliability flag |

#### Combined DataFrame (alignment_type="both")
Contains all columns from both global and local alignments, plus:
| Column | Type | Description |
|--------|------|-------------|
| type | str | Either 'global' or 'local' |

Rows will have `None` values for columns not applicable to their type.

## Attribution

This implementation is based on the original [cryoet-alignment repository](https://github.com/uermel/cryoet-alignment/blob/main/src/cryoet_alignment/io/aretomo3/aln.py) by **Utz H. Ermel**.

The original code is licensed under the MIT License. This implementation has been adapted and simplified to remove external dependencies and provide a more focused interface for reading AreTomo alignment files.