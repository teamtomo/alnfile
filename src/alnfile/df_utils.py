"""Utilities for converting alignment parameters to pandas DataFrames."""

import numpy as np
import pandas as pd

from .data_model import (
    PatchAlignmentParameters,
    TiltImageAlignmentParameters,
)


def global_alignments_to_dataframe(
    alignments: list[TiltImageAlignmentParameters],
) -> pd.DataFrame:
    """Convert list of TiltImageAlignmentParameters to pandas DataFrame.

    Parameters
    ----------
    alignments : list[TiltImageAlignmentParameters]
        List of global alignment parameters

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: sec, rot, gmag, tx, ty, smean, sfit, scale, base, tilt
    """
    data = {
        "sec": np.array([ga.sec for ga in alignments], dtype=np.int64),
        "rot": np.array([ga.rot for ga in alignments], dtype=np.float64),
        "gmag": np.array([ga.gmag for ga in alignments], dtype=np.float64),
        "tx": np.array([ga.tx for ga in alignments], dtype=np.float64),
        "ty": np.array([ga.ty for ga in alignments], dtype=np.float64),
        "smean": np.array([ga.smean for ga in alignments], dtype=np.float64),
        "sfit": np.array([ga.sfit for ga in alignments], dtype=np.float64),
        "scale": np.array([ga.scale for ga in alignments], dtype=np.float64),
        "base": np.array([ga.base for ga in alignments], dtype=np.float64),
        "tilt": np.array([ga.tilt for ga in alignments], dtype=np.float64),
    }
    return pd.DataFrame(data)


def local_alignments_to_dataframe(
    alignments: list[PatchAlignmentParameters],
) -> pd.DataFrame:
    """Convert list of PatchAlignmentParameters to pandas DataFrame."""
    data = {
        "sec_idx": np.array([la.sec_idx for la in alignments], dtype=np.int64),
        "patch_idx": np.array([la.patch_idx for la in alignments], dtype=np.int64),
        "center_x": np.array([la.center_x for la in alignments], dtype=np.float64),
        "center_y": np.array([la.center_y for la in alignments], dtype=np.float64),
        "shift_x": np.array([la.shift_x for la in alignments], dtype=np.float64),
        "shift_y": np.array([la.shift_y for la in alignments], dtype=np.float64),
        "is_reliable": np.array(
            [la.is_reliable for la in alignments], dtype=np.float64
        ),
    }
    return pd.DataFrame(data)
