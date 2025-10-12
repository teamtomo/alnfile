from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

GLOBAL_COLUMNS = ['sec', 'rot', 'gmag', 'tx', 'ty', 'smean', 'sfit', 'scale', 'base', 'tilt']
LOCAL_COLUMNS = ['sec_idx', 'patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']


class GlobalAlignmentInfo:
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

    __slots__ = ('sec', 'rot', 'gmag', 'tx', 'ty', 'smean', 'sfit', 'scale', 'base', 'tilt')

    FIELD_NAMES = GLOBAL_COLUMNS

    def __init__(self, sec: int, rot: float, gmag: float = 1.0, tx: float = 0.0, ty: float = 0.0,
                 smean: float = 1.0, sfit: float = 1.0, scale: float = 1.0, base: float = 0.0, tilt: float = 0.0
                 ):
        self.sec = sec
        self.rot = rot
        self.gmag = gmag
        self.tx = tx
        self.ty = ty
        self.smean = smean
        self.sfit = sfit
        self.scale = scale
        self.base = base
        self.tilt = tilt

    @property
    def field_names(self) -> list[str]:
        """Return field names for pandas DataFrame creation."""
        return self.FIELD_NAMES

    @classmethod
    def from_string(cls, line: str):
        """Parse global alignment """
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
        return iter(
            [self.sec, self.rot, self.gmag, self.tx, self.ty, self.smean, self.sfit, self.scale, self.base, self.tilt],
        )

    def __str__(self):
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

    def __repr__(self):
        return (f"GlobalAlignmentInfo(sec={self.sec}, rot={self.rot:.4f}, "
                f"tx={self.tx:.3f}, ty={self.ty:.3f}, tilt={self.tilt:.2f})")


class DarkFrameInfo:
    """Records metadata for tilt images excluded from reconstruction.

    Attributes:
        section_idx (int): Zero-indexed position in original acquisition order (pre-filtering).
        val2 (int): One-indexed position.
        angle (float): Nominal tilt angle for the excluded image (degrees).
    """

    __slots__ = ('section_idx', 'val2', 'angle')

    def __init__(self, section_idx: int, val2: int, angle: float):
        self.section_idx = section_idx
        self.val2 = val2
        self.angle = angle

    @classmethod
    def from_string(cls, line: str):
        parts = line.split("=")
        values = parts[1].split()
        section_idx = int(values[0])
        val2 = int(values[1])
        angle = float(values[2])
        return cls(section_idx=section_idx, val2=val2, angle=angle)

    def __iter__(self):
        return iter([self.section_idx, self.val2, self.angle])

    def __str__(self):
        return f"# DarkFrame ={self.section_idx:>6}{self.val2:>5}{self.angle:>9.2f}"

    def __repr__(self):
        return f"DarkFrameInfo(section_idx={self.section_idx}, val2={self.val2}, angle={self.angle:.2f})"


class LocalAlignmentInfo:
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

    __slots__ = ('sec_idx', 'patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable')

    FIELD_NAMES = LOCAL_COLUMNS

    def __init__(self, sec_idx: int, patch_idx: int, center_x: float, center_y: float,
                 shift_x: float, shift_y: float, is_reliable: float
                 ):
        self.sec_idx = sec_idx
        self.patch_idx = patch_idx
        self.center_x = center_x
        self.center_y = center_y
        self.shift_x = shift_x
        self.shift_y = shift_y
        self.is_reliable = is_reliable

    @property
    def field_names(self) -> list[str]:
        """Return field names for pandas DataFrame creation."""
        return self.FIELD_NAMES

    @classmethod
    def from_string(cls, line: str):
        """Parse local alignment."""
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

    def __str__(self):
        return (
            f"{self.sec_idx:>4}"
            f"{self.patch_idx:>4}"
            f"{self.center_x:>9.2f}"
            f"{self.center_y:>10.2f}"
            f"{self.shift_x:>10.2f}"
            f"{self.shift_y:>10.2f}"
            f"{self.is_reliable:>6.1f}"
        )

    def __repr__(self):
        return (f"LocalAlignmentInfo(sec_idx={self.sec_idx}, patch_idx={self.patch_idx}, "
                f"shift_x={self.shift_x:.2f}, shift_y={self.shift_y:.2f})")


class AreTomo3ALN:
    """Container for AreTomo3 .aln file data with global and patch-based alignment records.

    Attributes:
        header (str): File format identifier line (typically "# AreTomo Alignment").
        RawSize (tuple[int, int, int]): Original tilt series dimensions: width, height, number of tilts.
        NumPatches (int): Grid size for patch-based local alignment (0 = global only).
        DarkFrames (list[DarkFrameInfo]): Excluded tilt images removed during processing.
        AlphaOffset (float): Angular offset correction for sample tilt axis (degrees).
        BetaOffset (float): Angular offset correction for beam tilt axis (degrees).
        GlobalAlignments (list[GlobalAlignmentInfo]): Per-tilt rigid transformation parameters.
        LocalAlignments (list[LocalAlignmentInfo]): Per-patch deformation measurements.
    """

    def __init__(self, header: str | None = None, RawSize: tuple[int, int, int] | None = None,
                 NumPatches: int = 0, DarkFrames: list[DarkFrameInfo] | None = None,
                 AlphaOffset: float = 0.0, BetaOffset: float = 0.0,
                 GlobalAlignments: list[GlobalAlignmentInfo] | None = None,
                 LocalAlignments: list[LocalAlignmentInfo] | None = None
                 ):
        self.header = header or "# AreTomo Alignment / Priims bprmMn"
        self.RawSize = RawSize or (0, 0, 0)
        self.NumPatches = NumPatches
        self.DarkFrames = DarkFrames or []
        self.AlphaOffset = AlphaOffset if AlphaOffset is not None else 0.0
        self.BetaOffset = BetaOffset if BetaOffset is not None else 0.0
        self.GlobalAlignments = GlobalAlignments or []
        self.LocalAlignments = LocalAlignments or []

    @classmethod
    def from_string(cls, text: str) -> "AreTomo3ALN":
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
                    global_alignments.append(GlobalAlignmentInfo.from_string(line))
                elif section == "LocalAlignment":
                    local_alignments.append(LocalAlignmentInfo.from_string(line))
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
        dark_frames = "\n".join(map(str, self.DarkFrames))
        global_alignments = "\n".join(map(str, self.GlobalAlignments))
        local_alignments = "" if self.LocalAlignments is None else "\n".join(map(str, self.LocalAlignments))
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

    def get_global_alignments(self) -> pd.DataFrame:
        """Extract global alignment data as dataframe."""
        if not self.GlobalAlignments:
            raise ValueError("No global alignments found")
        data = {
            'sec': np.array([ga.sec for ga in self.GlobalAlignments], dtype=np.int64),
            'rot': np.array([ga.rot for ga in self.GlobalAlignments], dtype=np.float64),
            'gmag': np.array([ga.gmag for ga in self.GlobalAlignments], dtype=np.float64),
            'tx': np.array([ga.tx for ga in self.GlobalAlignments], dtype=np.float64),
            'ty': np.array([ga.ty for ga in self.GlobalAlignments], dtype=np.float64),
            'smean': np.array([ga.smean for ga in self.GlobalAlignments], dtype=np.float64),
            'sfit': np.array([ga.sfit for ga in self.GlobalAlignments], dtype=np.float64),
            'scale': np.array([ga.scale for ga in self.GlobalAlignments], dtype=np.float64),
            'base': np.array([ga.base for ga in self.GlobalAlignments], dtype=np.float64),
            'tilt': np.array([ga.tilt for ga in self.GlobalAlignments], dtype=np.float64),
        }
        return pd.DataFrame(data)


    def set_global_alignments(self, df: pd.DataFrame):
        """
        Set the global alignments from a pandas DataFrame.

        Args:
            df (pd.DataFrame): Global alignments as a pandas DataFrame.
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Invalid value type. Must be pandas.DataFrame")

        self.GlobalAlignments = [
            GlobalAlignmentInfo(
                sec=int(rec['sec']),
                rot=float(rec['rot']),
                gmag=float(rec['gmag']),
                tx=float(rec['tx']),
                ty=float(rec['ty']),
                smean=float(rec['smean']),
                sfit=float(rec['sfit']),
                scale=float(rec['scale']),
                base=float(rec['base']),
                tilt=float(rec['tilt'])
            )
            for rec in df.to_dict('records')
        ]


    def get_local_alignments(
        self,
        kind: Literal["pandas", "numpy"] = "pandas",
    ) -> pd.DataFrame | np.ndarray:
        """Extract local patch alignment data in tabular or array format.

        Args:
            kind (str): Output format - "pandas" for DataFrame, "numpy" for ndarray.

        Returns:
            pd.DataFrame | np.ndarray: Patch alignment with columns/fields:
                [sec_idx, patch_idx, center_x, center_y, shift_x, shift_y, is_reliable]
        """
        columns = LOCAL_COLUMNS

        if not self.LocalAlignments:
            if kind == "numpy":
                return np.empty((0, 7), dtype=np.float64)
            return pd.DataFrame(columns=columns)

        if kind == "numpy":
            data = np.array(
                [[la.sec_idx, la.patch_idx, la.center_x, la.center_y, la.shift_x, la.shift_y, la.is_reliable]
                 for la in self.LocalAlignments],
                dtype=np.float64
            )
            return data
        elif kind == "pandas":
            data = {
                'sec_idx': np.array([la.sec_idx for la in self.LocalAlignments], dtype=np.int64),
                'patch_idx': np.array([la.patch_idx for la in self.LocalAlignments], dtype=np.int64),
                'center_x': np.array([la.center_x for la in self.LocalAlignments], dtype=np.float64),
                'center_y': np.array([la.center_y for la in self.LocalAlignments], dtype=np.float64),
                'shift_x': np.array([la.shift_x for la in self.LocalAlignments], dtype=np.float64),
                'shift_y': np.array([la.shift_y for la in self.LocalAlignments], dtype=np.float64),
                'is_reliable': np.array([la.is_reliable for la in self.LocalAlignments], dtype=np.float64),
            }
            return pd.DataFrame(data)
        else:
            raise ValueError(f"kind must be 'pandas' or 'numpy', got '{kind}'")


    def set_local_alignments(self, values: pd.DataFrame):
        """
        Set the local alignments from a pandas DataFrame.

        Args:
            values (pd.DataFrame): Local alignments as a pandas DataFrame.
        """
        if not isinstance(values, pd.DataFrame):
            raise ValueError("Invalid value type. Must be pandas.DataFrame")

        self.LocalAlignments = [
            LocalAlignmentInfo(
                sec_idx=int(rec['sec_idx']),
                patch_idx=int(rec['patch_idx']),
                center_x=float(rec['center_x']),
                center_y=float(rec['center_y']),
                shift_x=float(rec['shift_x']),
                shift_y=float(rec['shift_y']),
                is_reliable=float(rec['is_reliable'])
            )
            for rec in values.to_dict('records')
        ]



    @classmethod
    def from_file(cls, file_path: Path) -> "AreTomo3ALN":
        """Load AreTomo3ALN from a file.

        Args:
            file_path: Path to the .aln file

        Returns:
            AreTomo3ALN object with parsed alignment data

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
