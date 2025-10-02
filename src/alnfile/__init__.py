"""
A Python package for reading AreTomo alignment files into pandas DataFrames.

Attribution:
    Based on the original cryoet-alignment repository by Utz H. Ermel:
    https://github.com/uermel/cryoet-alignment/blob/main/src/cryoet_alignment/io/aretomo3/aln.py
"""

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    # Fallback for systems with older Python (development/testing only)
    # Production requires Python 3.10+
    from importlib_metadata import PackageNotFoundError, version

from .reader import read

try:
    __version__ = version("alnfile")
except PackageNotFoundError:
    __version__ = "uninstalled"


__all__ = ["read"]
