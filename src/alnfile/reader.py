"""
Main reader module for AreTomo alignment files.

This module provides the parser for AreTomo alignment data
into pandas DataFrames.

Attribution:
    This implementation is based on the original work from the cryoet-alignment repository of Utz H. Ermel:
    https://github.com/uermel/cryoet-alignment/blob/main/src/cryoet_alignment/io/aretomo3/aln.py
    
    Original author: Utz H. Ermel
    Original license: MIT License
    
    This implementation has been adapted and simplified to remove external dependencies
    and provide a more focused interface for reading AreTomo alignment files.
"""

from pathlib import Path
import pandas as pd
import warnings


class GlobalAlignmentInfo:
    """Global alignment information for one section of a tilt series.

    Attributes:
        sec (int): Section index in the FINAL tilt series used for reconstruction, after removal of DarkFrames (0-based).
        rot (float): Tilt Axis Rotation angle in degrees.
        gmag (float): Magnification change.
        tx (float): X translation in pixels.
        ty (float): Y translation in pixels.
        smean (float): TBD
        sfit (float): TBD
        scale (float): TBD
        base (float): TBD
        tilt (float): Tilt angle in degrees.
    """

    def __init__(self, sec: int, rot: float, gmag: float = 1.0, tx: float = 0.0, ty: float = 0.0, 
                 smean: float = 1.0, sfit: float = 1.0, scale: float = 1.0, base: float = 0.0, tilt: float = 0.0):
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
        return ['sec', 'rot', 'gmag', 'tx', 'ty', 'smean', 'sfit', 'scale', 'base', 'tilt']

    @classmethod
    def from_string(cls, line: str):
        values = line.split()
        sec = int(values[0])
        rot = float(values[1])
        gmag = float(values[2])
        tx = float(values[3])
        ty = float(values[4])
        smean = float(values[5])
        sfit = float(values[6])
        scale = float(values[7])
        base = float(values[8])
        tilt = float(values[9])
        return cls(sec=sec, rot=rot, gmag=gmag, tx=tx, ty=ty, smean=smean, sfit=sfit, scale=scale, base=base, tilt=tilt)

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


class DarkFrameInfo:
    """Dark frame information for one section of a tilt series.

    Attributes:
        section_idx (int): Section index in the INPUT tilt series, before removal of DarkFrames (0-based).
        val2 (int): TBD
        angle (float): Tilt angle in degrees.
    """

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


class LocalAlignmentInfo:
    """Local alignment information for a patch on a section of a tilt series.

    Attributes:
        sec_idx (int): Section index in the FINAL tilt series used for reconstruction, after removal of DarkFrames
            (0-based).
        patch_idx (int): Patch index in the section (0-based).
        center_x (float): projected x coordinate of patch-subvolume wrp to section cetner (expected)
        center_y (float): projected y coordinate of patch-subvolume wrp to section cetner (expected)
        shift_x (float): x shift from expected patch center
        shift_y (float): y shift from expected patch center
        is_reliable (float): reliable/unrelaible flag
    """

    def __init__(self, sec_idx: int, patch_idx: int, center_x: float, center_y: float, 
                 shift_x: float, shift_y: float, is_reliable: float):
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
        return ['sec_idx', 'patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']

    @classmethod
    def from_string(cls, line: str):
        values = line.split()
        sec_idx = int(values[0])
        patch_idx = int(values[1])
        center_x = float(values[2])
        center_y = float(values[3])
        shift_x = float(values[4])
        shift_y = float(values[5])
        is_reliable = float(values[6])
        return cls(
            sec_idx=sec_idx,
            patch_idx=patch_idx,
            center_x=center_x,
            center_y=center_y,
            shift_x=shift_x,
            shift_y=shift_y,
            is_reliable=is_reliable,
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


class AreTomo3ALN:
    """AreTomo3's alignment file format (.aln). This file contains the global and local alignment information for a
    tilt series.

    Attributes:
        header (str): Header of the file. Should be "# AreTomo Alignment".
        RawSize (tuple[int, int, int]): Size of the tilt series in pixels (x, y) and sections (z).
        NumPatches (int): Number of patches for local alignment.
        DarkFrames (list[DarkFrameInfo]): List of dark frames (discarded for reconstruction).
        AlphaOffset (float): Alpha offset for the reconstruction.
        BetaOffset (float): Beta offset for the reconstruction.
        GlobalAlignments (list[GlobalAlignmentInfo]): List of global alignments.
        LocalAlignments (list[LocalAlignmentInfo]): List of local alignments.
    """

    def __init__(self, header: str | None = None, RawSize: tuple[int, int, int] | None = None, 
                 NumPatches: int = 0, DarkFrames: list[DarkFrameInfo] | None = None,
                 AlphaOffset: float = 0.0, BetaOffset: float = 0.0, 
                 GlobalAlignments: list[GlobalAlignmentInfo] | None = None,
                 LocalAlignments: list[LocalAlignmentInfo] | None = None):
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

        for _i, line in enumerate(lines):
            if line.startswith("# AreTomo Alignment"):
                header = line
                continue
            elif line.startswith("# RawSize"):
                raw_size = tuple(map(int, line.split("=")[1].split()))
                continue
            elif line.startswith("# NumPatches"):
                num_patches = int(line.split("=")[1])
                continue
            elif line.startswith("# DarkFrame"):
                dark_frames.append(DarkFrameInfo.from_string(line))
                continue
            elif line.startswith("# AlphaOffset"):
                alpha_offset = float(line.split("=")[1])
                continue
            elif line.startswith("# BetaOffset"):
                beta_offset = float(line.split("=")[1])
                continue
            elif line.startswith("# SEC"):
                section = "GlobalAlignment"
                continue
            elif line.startswith("# Local Alignment"):
                section = "LocalAlignment"
                continue

            if section == "GlobalAlignment":
                global_alignments.append(GlobalAlignmentInfo.from_string(line))
            elif section == "LocalAlignment":
                local_alignments.append(LocalAlignmentInfo.from_string(line))

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

    def get_global_alignments(
        self,
        kind: str = "pandas",
    ) -> pd.DataFrame:
        """Get the global alignments as a pandas DataFrame.

        Args:
            kind (str): Type of the output. Must be "pandas".

        Returns:
            pd.DataFrame: Global alignments as a pandas DataFrame with 10 columns.
        """
        if not self.GlobalAlignments:
            # Return empty DataFrame with correct columns
            columns = ['sec', 'rot', 'gmag', 'tx', 'ty', 'smean', 'sfit', 'scale', 'base', 'tilt']
            return pd.DataFrame(columns=columns)
        
        data = []
        for ga in self.GlobalAlignments:
            data.append([ga.sec, ga.rot, ga.gmag, ga.tx, ga.ty, ga.smean, ga.sfit, ga.scale, ga.base, ga.tilt])
        
        columns = ['sec', 'rot', 'gmag', 'tx', 'ty', 'smean', 'sfit', 'scale', 'base', 'tilt']
        return pd.DataFrame(data, columns=columns)

    def set_global_alignments(self, value: pd.DataFrame):
        """
        Set the global alignments from a pandas DataFrame.

        Args:
            value (pd.DataFrame): Global alignments as a pandas DataFrame.
        """
        global_alignments = []
        if isinstance(value, pd.DataFrame):
            for _, row in value.iterrows():
                global_alignments.append(
                    GlobalAlignmentInfo(
                        sec=int(row['sec']), rot=float(row['rot']), gmag=float(row['gmag']),
                        tx=float(row['tx']), ty=float(row['ty']), smean=float(row['smean']),
                        sfit=float(row['sfit']), scale=float(row['scale']), 
                        base=float(row['base']), tilt=float(row['tilt'])
                    )
                )
        else:
            raise ValueError("Invalid value type. Must be pandas.DataFrame")

        self.GlobalAlignments = global_alignments

    def get_local_alignments(
        self,
        kind: str = "pandas",
    ) -> pd.DataFrame:
        """Get the local alignments as a pandas DataFrame.

        Args:
            kind (str): Type of the output. Must be "pandas".

        Returns:
            pd.DataFrame: Local alignments as a pandas DataFrame with 7 columns.
        """
        if not self.LocalAlignments:
            # Return empty DataFrame with correct columns
            columns = ['sec_idx', 'patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']
            return pd.DataFrame(columns=columns)
        
        data = []
        for la in self.LocalAlignments:
            data.append([la.sec_idx, la.patch_idx, la.center_x, la.center_y, la.shift_x, la.shift_y, la.is_reliable])
        
        columns = ['sec_idx', 'patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']
        return pd.DataFrame(data, columns=columns)

    def set_local_alignments(self, values: pd.DataFrame):
        """
        Set the local alignments from a pandas DataFrame.

        Args:
            values (pd.DataFrame): Local alignments as a pandas DataFrame.
        """
        local_alignments = []
        if isinstance(values, pd.DataFrame):
            for _, row in values.iterrows():
                local_alignments.append(
                    LocalAlignmentInfo(
                        sec_idx=int(row['sec_idx']), patch_idx=int(row['patch_idx']),
                        center_x=float(row['center_x']), center_y=float(row['center_y']),
                        shift_x=float(row['shift_x']), shift_y=float(row['shift_y']),
                        is_reliable=float(row['is_reliable'])
                    )
                )
        else:
            raise ValueError("Invalid value type. Must be pandas.DataFrame")

        self.LocalAlignments = local_alignments

    def pandas(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get the global and local alignments as pandas DataFrames.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: Global and local alignments as pandas DataFrames
        """
        return self.get_global_alignments(), self.get_local_alignments()

    @classmethod
    def from_file(cls, file_path: Path) -> "AreTomo3ALN":
        """Load AreTomo3ALN from a file."""
        with open(file_path, 'r') as f:
            content = f.read()
        return cls.from_string(content)


def read(file: Path | str, alignment_type: str = "both") -> pd.DataFrame:
    """
    Read AreTomo alignment file and return a pandas DataFrame.
    
    Parameters
    ----------
    file : Path | str
        Path to the AreTomo alignment file (.aln)
    alignment_type : str, optional
        Type of alignment data to return. Options are:
        - "both": Return both global and local alignments (default)
        - "global": Return only global alignments
        - "local": Return only local alignments
        
    Returns
    -------
    pd.DataFrame
        DataFrame containing the alignment information. For "both", the DataFrame
        will contain a 'type' column indicating 'global' or 'local' alignment.
        
    Raises
    ------
    ValueError
        If alignment_type is not one of "both", "global", or "local"
        If the file does not exist or cannot be read
    """
    
    # Validate file exists
    file = Path(file)
    if not file.exists():
        raise ValueError(f"File does not exist: {file}")
    if not file.is_file():
        raise ValueError(f"Path is not a file: {file}")
        
    # Load the alignment data
    aln_data = AreTomo3ALN.from_file(file)
    
    # Check if local alignment data is available
    has_local_alignment = aln_data.NumPatches > 0 and len(aln_data.LocalAlignments) > 0
    
    # Use match-case statement (Python 3.10+ feature)
    match alignment_type:
        case "global":
            return aln_data.get_global_alignments()
        case "local":
            if not has_local_alignment:
                warnings.warn("Probably local alignment has not been performed (NumPatches=0 or no local alignment data found).")
                # Return empty DataFrame with correct columns
                columns = ['sec_idx', 'patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']
                return pd.DataFrame(columns=columns)
            return aln_data.get_local_alignments()
        case "both":
            global_df = aln_data.get_global_alignments()
            
            # Handle case where local alignment is not available
            if not has_local_alignment:
                warnings.warn("Probably local alignment has not been performed (NumPatches=0 or no local alignment data found). Returning only global alignments.")
                global_df['type'] = 'global'
                # Add empty columns for local alignment data
                for col in ['patch_idx', 'center_x', 'center_y', 'shift_x', 'shift_y', 'is_reliable']:
                    global_df[col] = None
                return global_df
            
            local_df = aln_data.get_local_alignments()
            
            # Add type column to distinguish between global and local alignments
            global_df['type'] = 'global'
            local_df['type'] = 'local'
            
            # Combine the DataFrames
            # Note: They have different columns, so we'll return them as separate sections
            # or we could create a unified structure - let's create a unified structure
            combined_data = []
            
            # Add global alignments
            for _, row in global_df.iterrows():
                combined_data.append({
                    'type': 'global',
                    'sec': row['sec'],
                    'rot': row['rot'],
                    'gmag': row['gmag'],
                    'tx': row['tx'],
                    'ty': row['ty'],
                    'smean': row['smean'],
                    'sfit': row['sfit'],
                    'scale': row['scale'],
                    'base': row['base'],
                    'tilt': row['tilt'],
                    'patch_idx': None,
                    'center_x': None,
                    'center_y': None,
                    'shift_x': None,
                    'shift_y': None,
                    'is_reliable': None
                })
            
            # Add local alignments
            for _, row in local_df.iterrows():
                combined_data.append({
                    'type': 'local',
                    'sec': row['sec_idx'],  # Map sec_idx to sec for consistency
                    'rot': None,
                    'gmag': None,
                    'tx': None,
                    'ty': None,
                    'smean': None,
                    'sfit': None,
                    'scale': None,
                    'base': None,
                    'tilt': None,
                    'patch_idx': row['patch_idx'],
                    'center_x': row['center_x'],
                    'center_y': row['center_y'],
                    'shift_x': row['shift_x'],
                    'shift_y': row['shift_y'],
                    'is_reliable': row['is_reliable']
                })
            
            return pd.DataFrame(combined_data)
        case _:
            raise ValueError("alignment_type must be one of 'both', 'global', or 'local'")