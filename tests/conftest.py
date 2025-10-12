from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def data_dir():
    """Return the test data directory."""
    return Path(__file__).parent.parent / "test_data"


@pytest.fixture
def file_with_local(data_dir):
    """Return path to test file with local alignment."""
    return data_dir / "global_and_local.aln"


@pytest.fixture
def file_no_local(data_dir):
    """Return path to test file without local alignment."""
    return data_dir / "global_no_local.aln"


@pytest.fixture
def simple_df():
    """Create a simple test DataFrame."""
    return pd.DataFrame({
        'sec': [0, 1, 2],
        'rot': [0.0, 45.0, -45.0],
        'gmag': [1.0, 1.0, 1.0],
        'tx': [0.0, 10.0, -5.0],
        'ty': [0.0, 5.0, 10.0],
        'smean': [1.0, 1.0, 1.0],
        'sfit': [1.0, 1.0, 1.0],
        'scale': [1.0, 1.0, 1.0],
        'base': [0.0, 0.0, 0.0],
        'tilt': [0.0, 30.0, -30.0]
    }
    )
