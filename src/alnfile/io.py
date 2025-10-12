import os
from pathlib import Path
from typing import Literal

import pandas as pd

from alnfile.data_model import AlnData
from alnfile.df_utils import (
    global_alignments_to_dataframe,
    local_alignments_to_dataframe,
)


def read(
    file: os.PathLike,
    alignment_type: Literal["global", "local"] = "global",
) -> pd.DataFrame:
    """
    Load AreTomo .aln file and extract alignment data.
    
    Parameters
    ----------
    file : Path | str
        Filesystem path to the .aln alignment file
    alignment_type : {"global", "local"}, default "global"
        Which alignment data to extract:
        - "global": Per-tilt rigid transformations
        - "local": Per-patch deformation data
        
    Returns
    -------
    pd.DataFrame
        Alignment parameters.
        
    Raises
    ------
    ValueError
        Invalid alignment_type, missing file, or unreadable file
    """

    # Validate if file exists
    file = Path(file)
    if not file.exists():
        raise ValueError(f"File does not exist: {file}")
    if not file.is_file():
        raise ValueError(f"Path is not a file: {file}")

    # Load the alignment data
    aln_file = AlnData.from_file(file)

    # Check if local alignment data is available
    has_local_alignment = aln_file.NumPatches > 0 and len(aln_file.LocalAlignments) > 0

    match alignment_type:
        case "global":
            return global_alignments_to_dataframe(aln_file.GlobalAlignments)
        case "local":
            if not has_local_alignment:
                raise ValueError(
                    "Local alignment has not been performed (NumPatches=0 or no local alignment data found)."
                )
            return local_alignments_to_dataframe(aln_file.LocalAlignments)
        case _:
            raise ValueError(f"alignment_type must be one of 'global', 'local'")
