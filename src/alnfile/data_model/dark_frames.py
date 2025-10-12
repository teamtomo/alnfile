from pydantic import BaseModel, ConfigDict


class DarkFrameInfo(BaseModel):
    """Records metadata for tilt images excluded from reconstruction.

    Attributes:
        section_idx (int): Zero-indexed position in original acquisition order (pre-filtering).
        val2 (int): One-indexed position.
        angle (float): Nominal tilt angle for the excluded image (degrees).
    """

    model_config = ConfigDict(frozen=False)

    section_idx: int
    val2: int
    angle: float

    @classmethod
    def from_string(cls, line: str) -> "DarkFrameInfo":
        """Parse dark frame info from string line."""
        parts = line.split("=")
        values = parts[1].split()
        section_idx = int(values[0])
        val2 = int(values[1])
        angle = float(values[2])
        return cls(section_idx=section_idx, val2=val2, angle=angle)

    def __iter__(self):
        """Allow iteration for compatibility."""
        return iter([self.section_idx, self.val2, self.angle])

    def to_aln_string(self) -> str:
        """Convert to .aln file format string."""
        return f"# DarkFrame ={self.section_idx:>6}{self.val2:>5}{self.angle:>9.2f}"
