import os
from pathlib import Path
import json
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import xarray as xr
from ..data.loader import WRFLoader
from ..detection.engelamiento import detect_engelamiento


class FrameExporter:
    """Exports WRF icing risk frames as SVG (high quality) and PNG (for web) with transparent backgrounds."""

    def __init__(self, loader: WRFLoader, output_dir: Path):
        self.loader = loader
        self.output_dir = output_dir
        self.frames_dir = output_dir / "frames"
        self.frames_dir.mkdir(parents=True, exist_ok=True)

    def _create_figure(self, dpi=300):
        """Create figure with transparent background."""
        fig = plt.figure(figsize=(10, 8), dpi=dpi)
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        ax.axis("off")
        return fig, ax

    def _plot_icing(self, ax, icing, lons, lats, extent):
        """Plot icing risk data on axes using Pressure (hPa)."""
        valid_mask = ~np.isnan(icing.values)
        if valid_mask.any():
            # Rango de presión: 250 hPa (superior) a 1000 hPa (inferior)
            # Usamos RdYlBu_r: Azul (baja presión/alto) -> Rojo (alta presión/bajo)
            levels = np.linspace(250, 1000, 16)
            ax.contourf(
                lons,
                lats,
                icing.values,
                levels=levels,
                cmap="RdYlBu_r",
                transform=ccrs.PlateCarree(),
                alpha=0.8,
                extend="both"
            )
        ax.set_extent(extent, crs=ccrs.PlateCarree())

    def export_all(self):
        """Iterates through all timesteps and exports frames for both top and bottom modes."""
        metadata = {"extent": None, "frames_top": [], "frames_bottom": []}

        num_times = self.loader.num_times
        print(f"Starting export of {num_times} timesteps (Top + Bottom modes)...")

        for i in range(num_times):
            data = self.loader.load_timestep(i)
            timestamp = str(self.loader.times.values[i])
            lons = data["XLONG"].values
            lats = data["XLAT"].values

            if metadata["extent"] is None:
                metadata["extent"] = [
                    float(lons.min()), float(lons.max()),
                    float(lats.min()), float(lats.max()),
                ]
            extent = metadata["extent"]

            for mode in ["top", "bottom"]:
                icing = detect_engelamiento(data, mode=mode)
                filename = f"frame_{mode}_{i:03d}.png"
                path = self.frames_dir / filename
                
                fig, ax = self._create_figure(dpi=150)
                self._plot_icing(ax, icing, lons, lats, extent)
                plt.savefig(path, format="png", transparent=True, bbox_inches="tight", pad_inches=0)
                plt.close(fig)

                frame_entry = {
                    "index": i,
                    "timestamp": timestamp,
                    "file": f"frames/{filename}"
                }
                if mode == "top":
                    metadata["frames_top"].append(frame_entry)
                else:
                    metadata["frames_bottom"].append(frame_entry)

            print(f"[{i + 1}/{num_times}] Exported frames for timestep {i}")

        # Save metadata for frontend
        metadata_path = self.output_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        print(f"Metadata saved to {metadata_path}")
