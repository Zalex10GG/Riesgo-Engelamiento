import numpy as np
import xarray as xr


def detect_engelamiento(data: dict, mode: str = "top") -> xr.DataArray:
    """
    Detecta pixeles con riesgo de engelamiento y devuelve la presión (hPa).
    (Volvemos a presión porque el archivo actual no tiene PH/PHB para calcular Z exacto).

    Args:
        data: Diccionario con variables WRF.
        mode: "top" para el nivel más alto (mínima presión), 
              "bottom" para el nivel más bajo (máxima presión).

    Returns:
        DataArray con presión (hPa) donde hay riesgo, NaN si no hay riesgo.
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

    # Para cada pixel (y,z): tomar el nivel según modo
    # "top" (superior) = menor presión (valor numérico mínimo)
    # "bottom" (inferior) = mayor presión (valor numérico máximo)
    if mode == "top":
        result = pressure_hpa.min(dim="bottom_top")
    else:
        result = pressure_hpa.max(dim="bottom_top")

    return result
