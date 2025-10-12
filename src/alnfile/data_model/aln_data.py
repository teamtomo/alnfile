from pathlib import Path

from pydantic import BaseModel, Field

from alnfile.data_model.global_alignments import TiltImageAlignmentParameters
from alnfile.data_model.local_alignments import PatchAlignmentParameters
from alnfile.data_model.dark_frames import DarkFrameInfo


class AlnData(BaseModel):
    """Data model for AreTomo3 .aln file data with global and patch-based alignment records.

    Attributes:
        header (str): File format identifier line (typically "# AreTomo Alignment").
        RawSize (tuple[int, int, int]): Original tilt series dimensions: width, height, number of tilts.
        NumPatches (int): Grid size for patch-based local alignment (0 = global only).
        DarkFrames (list[DarkFrameInfo]): Excluded tilt images removed during processing.
        AlphaOffset (float): Angular offset correction for sample tilt axis (degrees).
        BetaOffset (float): Angular offset correction for beam tilt axis (degrees).
        GlobalAlignments (list[TiltImageAlignmentParameters]): Per-tilt rigid transformation parameters.
        LocalAlignments (list[PatchAlignmentParameters]): Per-patch deformation measurements.
    """
    header: str = "# AreTomo Alignment / Priims bprmMn"
    RawSize: tuple[int, int, int] = (0, 0, 0)
    NumPatches: int = 0
    DarkFrames: list[DarkFrameInfo] = Field(default_factory=list)
    AlphaOffset: float = 0.0
    BetaOffset: float = 0.0
    GlobalAlignments: list[TiltImageAlignmentParameters] = Field(default_factory=list)
    LocalAlignments: list[PatchAlignmentParameters] = Field(default_factory=list)

    @classmethod
    def from_string(cls, text: str) -> "AlnData":
        """Parse AreTomo alignment file text."""
        text = text.strip()
        lines = text.splitlines()

        header = None
        raw_size = None
        num_patches = None
        dark_frames = []
        alpha_offset = None
        beta_offset = None
        global_alignments = []
        local_alignments = []
        section = None

        for line in lines:
            if not line or not line[0] == '#':
                if not line or line.isspace():
                    continue
                if section == "GlobalAlignment":
                    global_alignments.append(TiltImageAlignmentParameters.from_string(line))
                elif section == "LocalAlignment":
                    local_alignments.append(PatchAlignmentParameters.from_string(line))
                continue

            if line.startswith("# DarkFrame"):
                dark_frames.append(DarkFrameInfo.from_string(line))
            elif line.startswith("# SEC"):
                section = "GlobalAlignment"
            elif line.startswith("# Local Alignment"):
                section = "LocalAlignment"
            elif line.startswith("# RawSize"):
                raw_size = tuple(map(int, line.split("=", 1)[1].split()))
            elif line.startswith("# NumPatches"):
                num_patches = int(line.split("=", 1)[1])
            elif line.startswith("# AlphaOffset"):
                alpha_offset = float(line.split("=", 1)[1])
            elif line.startswith("# BetaOffset"):
                beta_offset = float(line.split("=", 1)[1])
            elif line.startswith("# AreTomo Alignment"):
                header = line

        return cls(
            header=header,
            RawSize=raw_size,
            NumPatches=num_patches,
            DarkFrames=dark_frames,
            AlphaOffset=alpha_offset,
            BetaOffset=beta_offset,
            GlobalAlignments=global_alignments,
            LocalAlignments=local_alignments,
        )

    def __str__(self) -> str:
        dark_frames = "\n".join(df.to_aln_string() for df in self.DarkFrames)
        global_alignments = "\n".join(ga.to_aln_string() for ga in self.GlobalAlignments)
        local_alignments = "" if self.LocalAlignments is None else "\n".join(
            la.to_aln_string() for la in self.LocalAlignments
        )
        return (
            f"{self.header}\n"
            f"# RawSize = {self.RawSize[0]} {self.RawSize[1]} {self.RawSize[2]}\n"
            f"# NumPatches = {self.NumPatches}\n"
            f"{dark_frames}\n"
            f"# AlphaOffset ={self.AlphaOffset:>9.2f}\n"
            f"# BetaOffset ={self.BetaOffset:>9.2f}\n"
            "# SEC     ROT         GMAG       TX          TY      SMEAN     SFIT    SCALE     BASE     TILT\n"
            f"{global_alignments}\n"
            "# Local Alignment\n"
            f"{local_alignments}\n"
        )

    @classmethod
    def from_file(cls, file_path: Path) -> "AlnData":
        """Load AlnFile from a file.

        Args:
            file_path: Path to the .aln file

        Returns:
            AlnFile object with parsed alignment data

        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If file has encoding issues
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with latin-1 encoding as fallback
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        return cls.from_string(content)
