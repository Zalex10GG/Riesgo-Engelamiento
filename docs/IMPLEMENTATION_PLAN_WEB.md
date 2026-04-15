# Glassmorphism Interface Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a professional glassmorphism web interface for aviation icing risk visualization, using PNG frames exported from Python and an interactive JS frontend.

**Architecture:** 
1. **Backend (Python):** Script to export all timesteps as PNGs (transparent backgrounds) and a `metadata.json` with timestamps and extent.
2. **Frontend (HTML/CSS/JS):** Modern UI with glassmorphism effects, a timeline slider, play/pause controls, and an OpenStreetMap base layer (using Leaflet.js for easier custom styling and overlay management).

**Tech Stack:** 
- Python: `xarray`, `matplotlib`, `cartopy`
- Frontend: HTML5, CSS3 (Flexbox/Grid, Backdrop-filter), Vanilla JS, Leaflet.js (for map)

---

## Chunk 1: Frame Exporter (Python)

**Files:**
- Create: `src/engelamiento/visualization/exporter.py`
- Modify: `main.py` (to use exporter)

- [ ] **Step 1: Create the exporter module**
Implement a class that iterates through all timesteps and saves each as a PNG with transparent background.

```python
import os
from pathlib import Path
import json
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
from ..data.loader import WRFLoader
from ..detection.engelamiento import detect_engelamiento

class FrameExporter:
    def __init__(self, loader: WRFLoader, output_dir: Path):
        self.loader = loader
        self.output_dir = output_dir
        self.frames_dir = output_dir / "frames"
        self.frames_dir.mkdir(parents=True, exist_ok=True)

    def export_all(self):
        metadata = {
            "extent": None,
            "frames": []
        }
        
        num_times = self.loader.num_times
        for i in range(num_times):
            data = self.loader.load_timestep(i)
            icing = detect_engelamiento(data)
            
            timestamp = str(self.loader.times.values[i])
            filename = f"frame_{i:03d}.png"
            filepath = self.frames_dir / filename
            
            # Use consistent figure settings for all frames
            fig = plt.figure(figsize=(10, 8), dpi=100)
            ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
            
            # Set transparent background
            fig.patch.set_alpha(0)
            ax.patch.set_alpha(0)
            ax.axis('off')
            
            lons = data["XLONG"].values
            lats = data["XLAT"].values
            
            if metadata["extent"] is None:
                metadata["extent"] = [
                    float(lons.min()), float(lons.max()),
                    float(lats.min()), float(lats.max())
                ]
            
            valid_mask = ~np.isnan(icing.values)
            if valid_mask.any():
                # Smooth contourf for "radar" look
                ax.contourf(lons, lats, icing.values, 
                            levels=np.linspace(800, 1000, 11),
                            cmap='RdYlBu_r', transform=ccrs.PlateCarree(),
                            alpha=0.8)
            
            ax.set_extent(metadata["extent"], crs=ccrs.PlateCarree())
            plt.savefig(filepath, transparent=True, bbox_inches='tight', pad_inches=0)
            plt.close(fig)
            
            metadata["frames"].append({
                "index": i,
                "timestamp": timestamp,
                "file": f"frames/{filename}"
            })
            print(f"Exported {filename} for {timestamp}")

        with open(self.output_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
```

- [ ] **Step 2: Run export**
Update `main.py` or create a temporary script to run the export.

---

## Chunk 2: Web Interface (HTML/CSS)

**Files:**
- Create: `templates/index.html`
- Create: `static/css/style.css`

- [ ] **Step 1: Create HTML structure**
Include Leaflet.js and containers for the map and glassmorphism panels.

- [ ] **Step 2: Apply glassmorphism CSS**
Use `backdrop-filter: blur(10px)` and semi-transparent backgrounds.

---

## Chunk 3: Frontend Logic (JS)

**Files:**
- Create: `static/js/app.js`

- [ ] **Step 1: Initialize Map and Load Metadata**
Fetch `metadata.json`, setup Leaflet map with Dark Matter tiles.

- [ ] **Step 2: Implement Animation Controller**
Handle slider updates, play/pause loop, and updating the image overlay on the map.

---

## Chunk 4: Verification

- [ ] **Step 1: Serve and Test**
Use `python -m http.server` in the root or `output` directory to verify the interface.
