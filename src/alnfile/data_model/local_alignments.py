from typing import ClassVar

from pydantic import BaseModel, ConfigDict

LOCAL_COLUMNS = ['sec_idx', 'patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']


class PatchAlignmentParameters(BaseModel):
    """Patch-based alignment data (local alignment)

    Attributes:
        sec_idx (int): Tilt position in final tilt series stack, zero-indexed (post dark frame removal).
        patch_idx (int): Sequential patch identifier within this tilt image (zero-indexed).
        center_x (float): Expected x position of patch center relative to image center (pixels).
        center_y (float): Expected y position of patch center relative to image center (pixels).
        shift_x (float): Measured x deviation from expected patch position (pixels).
        shift_y (float): Measured y deviation from expected patch position (pixels).
        is_reliable (float): Confidence flag for patch alignment quality (1.0=reliable, 0.0=unreliable).
    """

    model_config = ConfigDict(frozen=False)

    sec_idx: int
    patch_idx: int
    center_x: float
    center_y: float
    shift_x: float
    shift_y: float
    is_reliable: float

    FIELD_NAMES: ClassVar[list[str]] = LOCAL_COLUMNS

    @property
    def field_names(self) -> list[str]:
        """Return field names for pandas DataFrame creation."""
        return self.FIELD_NAMES

    @classmethod
    def from_string(cls, line: str) -> "PatchAlignmentParameters":
        """Parse local alignment from string line."""
        values = line.split()
        return cls(
            sec_idx=int(values[0]),
            patch_idx=int(values[1]),
            center_x=float(values[2]),
            center_y=float(values[3]),
            shift_x=float(values[4]),
            shift_y=float(values[5]),
            is_reliable=float(values[6])
        )

    def __iter__(self):
        """Allow iteration for DataFrame compatibility."""
        return iter(
            [
                self.sec_idx,
                self.patch_idx,
                self.center_x,
                self.center_y,
                self.shift_x,
                self.shift_y,
                self.is_reliable,
            ],
        )

    def to_aln_string(self) -> str:
        """Convert to .aln file format string."""
        return (
            f"{self.sec_idx:>4}"
            f"{self.patch_idx:>4}"
            f"{self.center_x:>9.2f}"
            f"{self.center_y:>10.2f}"
            f"{self.shift_x:>10.2f}"
            f"{self.shift_y:>10.2f}"
            f"{self.is_reliable:>6.1f}"
        )

    def __repr__(self) -> str:
        """Return string representation."""
        return (f"LocalAlignmentParameters(sec_idx={self.sec_idx}, patch_idx={self.patch_idx}, "
                f"shift_x={self.shift_x:.2f}, shift_y={self.shift_y:.2f})")
