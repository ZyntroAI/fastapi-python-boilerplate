import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from enum import Enum
from pathlib import Path


class SpectralIndex(str, Enum):
    NDVI = "ndvi"   # vegetation: (NIR - Red) / (NIR + Red)
    NDBI = "ndbi"   # built-up:   (SWIR - NIR) / (SWIR + NIR)
    NDWI = "ndwi"   # water:      (Green - NIR) / (Green + NIR)


# ---------- Step 1: Preprocessing (align + radiometric normalize) ----------
def align_to_reference(src_path: str, ref_path: str, out_path: str) -> None:
    """Co-register src raster to ref's CRS, transform, and grid."""
    with rasterio.open(ref_path) as ref, rasterio.open(src_path) as src:
        meta = ref.meta.copy()
        with rasterio.open(out_path, "w", **meta) as dst:
            for band in range(1, ref.count + 1):
                reproject(
                    source=rasterio.band(src, band),
                    destination=rasterio.band(dst, band),
                    src_transform=src.transform, src_crs=src.crs,
                    dst_transform=ref.transform, dst_crs=ref.crs,
                    resampling=Resampling.bilinear,
                )


# ---------- Step 2: SpectralIndex tool equivalent ----------
BANDS = {  # typical Sentinel-2 / Landsat band positions in a stacked GeoTIFF
    "blue": 1, "green": 2, "red": 3, "nir": 4, "swir": 5,
}

def compute_index(raster_path: str, index: SpectralIndex) -> tuple[np.ndarray, dict]:
    with rasterio.open(raster_path) as ds:
        def b(name): return ds.read(BANDS[name]).astype(np.float32)
        red, nir, green, swir = b("red"), b("nir"), b("green"), b("swir")
        if index == SpectralIndex.NDVI:
            idx = (nir - red) / (nir + red + 1e-10)
        elif index == SpectralIndex.NDBI:
            idx = (swir - nir) / (swir + nir + 1e-10)
        else:  # NDWI (McFeeters)
            idx = (green - nir) / (green + nir + 1e-10)
        return np.clip(idx, -1, 1), ds.profile


# ---------- Steps 3–4: Difference + RasterThresholdClassification ----------
def detect_change(base_idx: np.ndarray, target_idx: np.ndarray,
                  threshold: float = 0.2) -> np.ndarray:
    """Δ = target − base. Returns int8: +1=gain, -1=loss, 0=no change."""
    delta = target_idx - base_idx
    out = np.zeros(delta.shape, dtype=np.int8)
    out[delta > threshold] = 1    # gain  (e.g. vegetation increase)
    out[delta < -threshold] = -1  # loss
    return out


# ---------- Step 5: Color-coded change map (Red=loss, Green=gain, Gray=none) ----------
CHANGE_RGB = {-1: (220, 38, 38), 0: (180, 180, 180), 1: (22, 163, 74)}

def to_color_map(classified: np.ndarray, profile: dict, out_path: str) -> None:
    rgb = np.zeros((3, *classified.shape), dtype=np.uint8)
    for cls, (r, g, b) in CHANGE_RGB.items():
        mask = classified == cls
        rgb[0][mask], rgb[1][mask], rgb[2][mask] = r, g, b
    meta = {**profile, "count": 3, "dtype": "uint8", "driver": "GTiff"}
    with rasterio.open(out_path, "w", **meta) as dst:
        dst.write(rgb)
