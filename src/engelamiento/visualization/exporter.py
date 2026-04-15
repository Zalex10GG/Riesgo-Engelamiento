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
        """Plot icing risk data on axes."""
        valid_mask = ~np.isnan(icing.values)
        if valid_mask.any():
            levels = np.linspace(800, 1000, 11)
            ax.contourf(
                lons,
                lats,
                icing.values,
                levels=levels,
                cmap="RdYlBu_r",
                transform=ccrs.PlateCarree(),
                alpha=0.8,
            )
        ax.set_extent(extent, crs=ccrs.PlateCarree())

    def export_all(self):
        """Iterates through all timesteps and exports both SVG and PNG frames."""
        metadata = {"extent": None, "frames": []}

        num_times = self.loader.num_times
        print(f"Starting export of {num_times} frames (SVG + PNG)...")

        for i in range(num_times):
            data = self.loader.load_timestep(i)
            icing = detect_engelamiento(data)

            timestamp = str(self.loader.times.values[i])

            lons = data["XLONG"].values
            lats = data["XLAT"].values

            # Capture extent on first frame
            if metadata["extent"] is None:
                metadata["extent"] = [
                    float(lons.min()),
                    float(lons.max()),
                    float(lats.min()),
                    float(lats.max()),
                ]

            extent = metadata["extent"]

            # Export SVG (high quality for static use)
            svg_filename = f"frame_{i:03d}.svg"
            svg_path = self.frames_dir / svg_filename
            fig, ax = self._create_figure(dpi=150)
            self._plot_icing(ax, icing, lons, lats, extent)
            plt.savefig(
                svg_path,
                format="svg",
                transparent=True,
                bbox_inches="tight",
                pad_inches=0,
            )
            plt.close(fig)

            # Export PNG (for web interface - high resolution)
            png_filename = f"frame_{i:03d}.png"
            png_path = self.frames_dir / png_filename
            fig, ax = self._create_figure(dpi=150)
            self._plot_icing(ax, icing, lons, lats, extent)
            plt.savefig(
                png_path,
                format="png",
                transparent=True,
                bbox_inches="tight",
                pad_inches=0,
            )
            plt.close(fig)

            metadata["frames"].append(
                {
                    "index": i,
                    "timestamp": timestamp,
                    "file": f"frames/{png_filename}",
                    "file_svg": f"frames/{svg_filename}",
                }
            )
            print(f"[{i + 1}/{num_times}] Exported {svg_filename} + {png_filename}")

        # Save metadata for frontend
        metadata_path = self.output_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        print(f"Metadata saved to {metadata_path}")
