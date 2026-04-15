import numpy as np
import xarray as xr
import sys
from pathlib import Path

# Añadir src al path para los tests
sys.path.append(str(Path(__file__).parent.parent / "src"))

from engelamiento.detection.engelamiento import detect_engelamiento


def test_engelamiento_detected():
    """Test: pixel con T<0 y agua líquida tiene engelamiento."""
    # Simular un dataset con 1 pixel en horizontal y 1 nivel vertical
    data = {
        "TK": xr.DataArray(
            np.array([[[260.0]]]), dims=("bottom_top", "south_north", "west_east")
        ),  # Bajo cero
        "P": xr.DataArray(
            np.array([[[1000.0]]]), dims=("bottom_top", "south_north", "west_east")
        ),  # Pa
        "PB": xr.DataArray(
            np.array([[[90000.0]]]), dims=("bottom_top", "south_north", "west_east")
        ),  # Pa
        "QRAIN": xr.DataArray(
            np.array([[[0.001]]]), dims=("bottom_top", "south_north", "west_east")
        ),  # Agua líquida
        "QCLOUD": xr.DataArray(
            np.array([[[0.0]]]), dims=("bottom_top", "south_north", "west_east")
        ),
    }

    result = detect_engelamiento(data)
    # result debe ser 2D (south_north, west_east)
    assert not np.isnan(result.values).all()
    # 91000 Pa = 910 hPa
    assert np.isclose(result.values.flat[0], 910.0)


def test_no_engelamiento_warm():
    """Test: pixel con T>0 no tiene engelamiento."""
    data = {
        "TK": xr.DataArray(
            np.array([[[280.0]]]), dims=("bottom_top", "south_north", "west_east")
        ),  # Sobre cero
        "P": xr.DataArray(
            np.array([[[1000.0]]]), dims=("bottom_top", "south_north", "west_east")
        ),
        "PB": xr.DataArray(
            np.array([[[90000.0]]]), dims=("bottom_top", "south_north", "west_east")
        ),
        "QRAIN": xr.DataArray(
            np.array([[[0.001]]]), dims=("bottom_top", "south_north", "west_east")
        ),
        "QCLOUD": xr.DataArray(
            np.array([[[0.0]]]), dims=("bottom_top", "south_north", "west_east")
        ),
    }

    result = detect_engelamiento(data)
    assert np.isnan(result.values.flat[0])


def test_no_engelamiento_no_liquid():
    """Test: pixel con T<0 pero sin agua líquida."""
    data = {
        "TK": xr.DataArray(
            np.array([[[260.0]]]), dims=("bottom_top", "south_north", "west_east")
        ),
        "P": xr.DataArray(
            np.array([[[1000.0]]]), dims=("bottom_top", "south_north", "west_east")
        ),
        "PB": xr.DataArray(
            np.array([[[90000.0]]]), dims=("bottom_top", "south_north", "west_east")
        ),
        "QRAIN": xr.DataArray(
            np.array([[[0.0]]]), dims=("bottom_top", "south_north", "west_east")
        ),
        "QCLOUD": xr.DataArray(
            np.array([[[0.0]]]), dims=("bottom_top", "south_north", "west_east")
        ),
    }

    result = detect_engelamiento(data)
    assert np.isnan(result.values.flat[0])
