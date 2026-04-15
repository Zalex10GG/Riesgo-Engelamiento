import numpy as np
import xarray as xr


def detect_engelamiento(data: dict) -> xr.DataArray:
    """
    Detecta pixeles con riesgo de engelamiento.

    Engelamiento: TK < 273.15 K AND (QRAIN > 0 OR QCLOUD > 0)

    Returns:
        DataArray con presión (hPa) donde hay riesgo, NaN si no hay riesgo.
        Si múltiples niveles, toma el de menor presión (mayor altitud).
    """
    TK = data["TK"]
    P = data["P"] + data["PB"]  # Presión total en Pa
    QRAIN = data["QRAIN"]
    QCLOUD = data["QCLOUD"]

    # Condiciones de engelamiento
    below_zero = TK < 273.15  # Kelvin
    liquid_water = (QRAIN > 0) | (QCLOUD > 0)
    engelamiento_mask = below_zero & liquid_water

    # Aplicar máscara y convertir a hPa
    pressure_hpa = (P / 100.0).where(engelamiento_mask)

    # Para cada pixel (y,z): tomar el nivel de menor presión (mayor altitud)
    # Dimensión bottom_top es la vertical
    result = pressure_hpa.min(dim="bottom_top")

    return result
