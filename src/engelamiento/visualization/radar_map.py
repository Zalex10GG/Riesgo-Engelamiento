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
    Genera mapa radar-style del riesgo de engelamiento con contornos suavizados.

    Color representa la presión (hPa) del nivel con engelamiento.
    """
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    lons_data = lons.values
    lats_data = lats.values
    pressure_data = engelamiento_pressure.values

    # Añadir features geográficos - Fondo limpio
    ax.add_feature(cfeature.LAND, facecolor="#f5f5f5", zorder=1)
    ax.add_feature(cfeature.COASTLINE, edgecolor="#444444", linewidth=0.8, zorder=3)
    ax.add_feature(cfeature.BORDERS, linestyle=":", edgecolor="#666666", zorder=3)
    ax.add_feature(cfeature.LAKES, alpha=0.3, zorder=1)
    ax.add_feature(cfeature.RIVERS, alpha=0.3, zorder=1)

    # Verificar si hay datos válidos
    valid_mask = ~np.isnan(pressure_data)

    if np.any(valid_mask):
        vmin, vmax = np.nanmin(pressure_data), np.nanmax(pressure_data)

        # Usamos contourf para un suavizado meteorológico profesional (look radar)
        # 25 niveles para un degradado muy suave
        levels = np.linspace(vmin, vmax, 25)
        cmap = "RdYlBu_r"

        cntr = ax.contourf(
            lons_data,
            lats_data,
            pressure_data,
            levels=levels,
            transform=ccrs.PlateCarree(),
            cmap=cmap,
            alpha=0.85,
            zorder=2,
            extend="both",
        )

        # Opcional: Contornos finos para dar profundidad
        ax.contour(
            lons_data,
            lats_data,
            pressure_data,
            levels=levels[::5],  # Solo algunos niveles
            colors="white",
            linewidths=0.3,
            alpha=0.2,
            transform=ccrs.PlateCarree(),
            zorder=2.5,
        )

        # Colorbar
        cbar = plt.colorbar(
            cntr,
            ax=ax,
            orientation="vertical",
            shrink=0.7,
            label="Presión (hPa)",
            pad=0.05,
        )
        cbar.ax.tick_params(labelsize=10)
    else:
        ax.text(
            0.5,
            0.5,
            "SIN RIESGO DETECTADO",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=20,
            color="gray",
            alpha=0.5,
        )

    # Extensión del mapa basada en los datos
    ax.set_extent(
        [lons_data.min(), lons_data.max(), lats_data.min(), lats_data.max()],
        crs=ccrs.PlateCarree(),
    )

    ax.set_title(title, pad=20, fontsize=15, fontweight="bold")
    ax.gridlines(
        draw_labels=True,
        dms=True,
        x_inline=False,
        y_inline=False,
        linestyle="--",
        alpha=0.3,
        zorder=4,
    )

    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()
