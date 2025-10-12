"""
A Python package for reading AreTomo alignment files into pandas DataFrames.

Attribution:
    Based on the original cryoet-alignment repository by Utz H. Ermel:
    https://github.com/uermel/cryoet-alignment/blob/main/src/cryoet_alignment/io/aretomo3/aln.py
"""

from importlib.metadata import PackageNotFoundError, version

from .df_utils import (
    global_alignments_to_dataframe,
    local_alignments_to_dataframe,
)
from .imod_utils import df_to_xf
from .io import read

try:
    __version__ = version("alnfile")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = [
    "read",
    "df_to_xf",
    "global_alignments_to_dataframe",
    "local_alignments_to_dataframe",
    "__version__",
]
