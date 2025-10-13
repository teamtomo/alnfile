from typing import ClassVar

from pydantic import BaseModel

GLOBAL_COLUMNS = ['sec', 'rot', 'gmag', 'tx', 'ty', 'smean', 'sfit', 'scale', 'base', 'tilt']


class TiltImageAlignmentParameters(BaseModel):
    """Stores per-tilt global alignment parameters from AreTomo processing.

    Attributes:
        sec (int): Zero-indexed position in the final aligned stack (excludes dark frames).
        rot (float): Rotation angle of the tilt axis relative to Y-axis (degrees).
        gmag (float): Global magnification adjustment factor.
        tx (float): X shift (pixels).
        ty (float): Y shift (pixels).
        smean (float): Statistical metric (implementation-specific, see AreTomo docs).
        sfit (float): Statistical metric (implementation-specific, see AreTomo docs).
        scale (float): Scaling parameter for this tilt.
        base (float): (implementation-specific, see AreTomo docs).
        tilt (float): Nominal tilt angle (degrees).
    """
    sec: int
    rot: float
    gmag: float = 1.0
    tx: float = 0.0
    ty: float = 0.0
    smean: float = 1.0
    sfit: float = 1.0
    scale: float = 1.0
    base: float = 0.0
    tilt: float = 0.0

    FIELD_NAMES: ClassVar[list[str]] = GLOBAL_COLUMNS

    @property
    def field_names(self) -> list[str]:
        """Return ordered field names for pandas DataFrame creation."""
        return self.FIELD_NAMES

    @classmethod
    def from_string(cls, line: str) -> "TiltImageAlignmentParameters":
        """Parse global alignment from string line."""
        values = line.split()
        return cls(
            sec=int(values[0]),
            rot=float(values[1]),
            gmag=float(values[2]),
            tx=float(values[3]),
            ty=float(values[4]),
            smean=float(values[5]),
            sfit=float(values[6]),
            scale=float(values[7]),
            base=float(values[8]),
            tilt=float(values[9])
        )

    def __iter__(self):
        """Allow iteration for DataFrame compatibility."""
        return iter(
            [self.sec, self.rot, self.gmag, self.tx, self.ty, self.smean, self.sfit, self.scale, self.base, self.tilt],
        )

    def to_aln_string(self) -> str:
        """Convert to .aln file format string."""
        return (
            f"{self.sec:>5}"
            f"{self.rot:>11.4f}"
            f"{self.gmag:>11.5f}"
            f"{self.tx:>11.3f}"
            f"{self.ty:>11.3f}"
            f"{self.smean:>9.2f}"
            f"{self.sfit:>9.2f}"
            f"{self.scale:>9.2f}"
            f"{self.base:>9.2f}"
            f"{self.tilt:>10.2f}"
        )

    def __repr__(self) -> str:
        """Return string representation."""
        return (f"GlobalAlignmentParameters(sec={self.sec}, rot={self.rot:.4f}, "
                f"tx={self.tx:.3f}, ty={self.ty:.3f}, tilt={self.tilt:.2f})")
