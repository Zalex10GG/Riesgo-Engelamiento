import xarray as xr
from pathlib import Path
from typing import Optional


class WRFLoader:
    """Carga lazy de datos WRF para un timestep específico."""

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        self._ds: Optional[xr.Dataset] = None

    def _open_dataset(self) -> xr.Dataset:
        if self._ds is None:
            self._ds = xr.open_dataset(self.filepath)
        return self._ds

    def load_timestep(self, time_idx: int = 0) -> dict:
        """Carga solo el timestep especificado."""
        ds = self._open_dataset()
        return {
            "TK": ds["TK"].isel(Time=time_idx),
            "P": ds["P"].isel(Time=time_idx),
            "PB": ds["PB"].isel(Time=time_idx),
            "XLAT": ds["XLAT"].isel(Time=time_idx),
            "XLONG": ds["XLONG"].isel(Time=time_idx),
            "QRAIN": ds["QRAIN"].isel(Time=time_idx),
            "QCLOUD": ds["QCLOUD"].isel(Time=time_idx),
        }

    @property
    def num_times(self) -> int:
        return len(self._open_dataset()["Time"])

    @property
    def times(self) -> xr.DataArray:
        return self._open_dataset()["XTIME"]
