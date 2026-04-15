# Engelamiento Radar Map - Plan de Implementación

**Goal:** Generar un mapa estático (PNG) mostrando pixeles con riesgo de engelamiento usando cartopy.

**Architecture:** SRE en Python con estructura modular (data/detection/visualization)

**Tech Stack:** xarray, numpy, matplotlib, cartopy

---

## Chunk 1: Estructura del Proyecto y Dependencias

**Files:**
- Create: `src/engelamiento/__init__.py`
- Create: `src/engelamiento/data/__init__.py`
- Create: `src/engelamiento/data/loader.py`
- Create: `src/engelamiento/detection/__init__.py`
- Create: `src/engelamiento/detection/engelamiento.py`
- Create: `src/engelamiento/visualization/__init__.py`
- Create: `src/engelamiento/visualization/radar_map.py`

- [ ] **Step 1: Crear estructura de directorios**

```bash
mkdir -p src/engelamiento/data src/engelamiento/detection src/engelamiento/visualization output
```

- [ ] **Step 2: Crear `src/engelamiento/__init__.py`**

```python
"""Engelamiento radar map application."""
```

- [ ] **Step 3: Crear `src/engelamiento/data/__init__.py`**

```python
"""Data loading module."""
from .loader import WRFLoader

__all__ = ["WRFLoader"]
```

- [ ] **Step 4: Crear `src/engelamiento/detection/__init__.py`**

```python
"""Engelamiento detection module."""
from .engelamiento import detect_engelamiento

__all__ = ["detect_engelamiento"]
```

- [ ] **Step 5: Crear `src/engelamiento/visualization/__init__.py`**

```python
"""Visualization module."""
from .radar_map import plot_engelamiento_map

__all__ = ["plot_engelamiento_map"]
```

- [ ] **Step 6: Actualizar `pyproject.toml`** con script entry point

```toml
[project.scripts]
engelamiento = "engelamiento.main:main"
```

- [ ] **Step 7: Commit**

```bash
git add src/ pyproject.toml
git commit -m "feat: add project structure and modules"
```

---

## Chunk 2: Data Loader (Lazy Loading)

**Files:**
- Modify: `src/engelamiento/data/loader.py`

- [ ] **Step 1: Implementar WRFLoader con lazy loading**

```python
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
            self._ds = xr.open_dataset(self.filepath, chunks={"Time": 1})
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
```

- [ ] **Step 2: Commit**

```bash
git add src/engelamiento/data/loader.py
git commit -m "feat: add WRFLoader with lazy loading"
```

---

## Chunk 3: Detección de Engelamiento

**Files:**
- Modify: `src/engelamiento/detection/engelamiento.py`

- [ ] **Step 1: Implementar detección**

```python
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
    pressure_hpa = (P * engelamiento_mask / 100).where(engelamiento_mask)
    
    # Para cada pixel (y,z): tomar el nivel de menor presión (mayor altitud)
    result = pressure_hpa.min(dim="bottom_top")
    
    return result
```

- [ ] **Step 2: Commit**

```bash
git add src/engelamiento/detection/engelamiento.py
git commit -m "feat: add engelamiento detection logic"
```

---

## Chunk 4: Visualización con Cartopy

**Files:**
- Modify: `src/engelamiento/visualization/radar_map.py`

- [ ] **Step 1: Implementar plot_engelamiento_map**

```python
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable


def plot_engelamiento_map(
    engelamiento_pressure: "xr.DataArray",
    lats: "xr.DataArray",
    lons: "xr.DataArray",
    output_path: str,
    title: str = "Riesgo de Engelamiento",
) -> None:
    """
    Genera mapa radar-style del riesgo de engelamiento.
    
    Color representa la presión (hPa) del nivel con engelamiento.
    """
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    
    lons_data = lons.values
    lats_data = lats.values
    pressure_data = engelamiento_pressure.values
    
    # Añadir features geográficos
    ax.add_feature(cfeature.LAND, facecolor="lightgray")
    ax.add_feature(cfeature.OCEAN, facecolor="lightblue")
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=":")
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS)
    
    # Plot con pcolormesh para suavizado
    # Excluir NaN para el rango del colorbar
    valid_data = pressure_data[~np.isnan(pressure_data)]
    
    if len(valid_data) > 0:
        vmin, vmax = np.nanmin(valid_data), np.nanmax(valid_data)
        norm = Normalize(vmin=vmin, vmax=vmax)
        
        mesh = ax.pcolormesh(
            lons_data,
            lats_data,
            pressure_data,
            transform=ccrs.PlateCarree(),
            cmap="coolwarm",
            norm=norm,
            shading="auto",
        )
        
        # Colorbar
        cbar = plt.colorbar(
            ScalarMappable(norm=norm, cmap="coolwarm"),
            ax=ax,
            orientation="vertical",
            shrink=0.8,
            label="Presión (hPa)",
        )
    else:
        ax.set_title("Sin riesgo de engelamiento detectado")
    
    # Extensión del mapa
    ax.set_extent([
        lons_data.min(), lons_data.max(),
        lats_data.min(), lats_data.max()
    ], crs=ccrs.PlateCarree())
    
    ax.set_title(title)
    ax.gridlines(draw_labels=True)
    
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
```

- [ ] **Step 2: Commit**

```bash
git add src/engelamiento/visualization/radar_map.py
git commit -m "feat: add radar-style map visualization with cartopy"
```

---

## Chunk 5: Main Script

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Implementar main.py**

```python
from pathlib import Path
from engelamiento.data.loader import WRFLoader
from engelamiento.detection.engelamiento import detect_engelamiento
from engelamiento.visualization.radar_map import plot_engelamiento_map


def main():
    DATA_PATH = Path("Data/wrfout_d01_2015-04-17_18_00_00_corte.nc")
    OUTPUT_DIR = Path("output")
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    TIME_IDX = 0  # Primera hora
    
    loader = WRFLoader(DATA_PATH)
    data = loader.load_timestep(time_idx=TIME_IDX)
    
    engelamiento = detect_engelamiento(data)
    
    output_path = OUTPUT_DIR / "engelamiento_map.png"
    plot_engelamiento_map(
        engelamiento_pressure=engelamiento,
        lats=data["XLAT"],
        lons=data["XLONG"],
        output_path=output_path,
        title=f"Riesgo de Engelamiento - {loader.times.values[TIME_IDX]}",
    )
    print(f"Mapa guardado en: {output_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add main.py
git commit -m "feat: add main script for engelamiento radar map"
```

---

## Chunk 6: Test y Verificación

**Files:**
- Create: `tests/test_detection.py`

- [ ] **Step 1: Crear test básico**

```python
import numpy as np
from engelamiento.detection.engelamiento import detect_engelamiento


def test_engelamiento_detected():
    """Test: pixel con T<0 y agua líquida tiene engelamiento."""
    data = {
        "TK": np.array([[[260.0]]]),  # Bajo cero
        "P": np.array([[[1000.0]]]),  # Pa
        "PB": np.array([[[90000.0]]]),  # Pa
        "QRAIN": np.array([[[0.001]]]),  # Agua líquida
        "QCLOUD": np.array([[[0.0]]]),
    }
    
    result = detect_engelamiento(data)
    assert not np.isnan(result.values).all()
    # 91000 Pa = 910 hPa
    assert np.isclose(result.values.flat[0], 910.0)


def test_no_engelamiento_warm():
    """Test: pixel con T>0 no tiene engelamiento."""
    data = {
        "TK": np.array([[[280.0]]]),  # Sobre cero
        "P": np.array([[[1000.0]]]),
        "PB": np.array([[[90000.0]]]),
        "QRAIN": np.array([[[0.001]]]),
        "QCLOUD": np.array([[[0.0]]]),
    }
    
    result = detect_engelamiento(data)
    assert np.isnan(result.values.flat[0])


def test_no_engelamiento_no_liquid():
    """Test: pixel con T<0 pero sin agua líquida."""
    data = {
        "TK": np.array([[[260.0]]]),
        "P": np.array([[[1000.0]]]),
        "PB": np.array([[[90000.0]]]),
        "QRAIN": np.array([[[0.0]]]),
        "QCLOUD": np.array([[[0.0]]]),
    }
    
    result = detect_engelamiento(data)
    assert np.isnan(result.values.flat[0])
```

- [ ] **Step 2: Añadir pytest y ejecutar tests**

```bash
uv add --dev pytest
uv run pytest tests/ -v
```

- [ ] **Step 3: Commit**

```bash
git add tests/ pyproject.toml
git commit -m "test: add unit tests for engelamiento detection"
```

---

## Chunk 7: Ejecución Final

- [ ] **Step 1: Generar mapa**

```bash
uv run python main.py
```

- [ ] **Step 2: Verificar output en `output/engelamiento_map.png`**

- [ ] **Step 3: Commit final**

```bash
git add output/
git commit -m "feat: generate first engelamiento radar map"
```

---

## Resumen de Commits

1. `chore: initial project setup with WRF data`
2. `feat: add project structure and modules`
3. `feat: add WRFLoader with lazy loading`
4. `feat: add engelamiento detection logic`
5. `feat: add radar-style map visualization with cartopy`
6. `feat: add main script for engelamiento radar map`
7. `test: add unit tests for engelamiento detection`
8. `feat: generate first engelamiento radar map`
