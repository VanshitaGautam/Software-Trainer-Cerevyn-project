"""Core NDVI calculations and reproducible date-to-date comparison."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import numpy as np


@dataclass
class ComparisonResult:
    summary: dict[str, Any]
    ndvi_before: np.ndarray
    ndvi_after: np.ndarray
    delta: np.ndarray
    shared_valid_mask: np.ndarray


def _as_2d(name: str, values: Any) -> np.ndarray:
    arr = np.asarray(values)
    if arr.ndim != 2 or arr.size == 0:
        raise ValueError(f"{name} must be a non-empty 2D array")
    return arr


def calculate_ndvi(nir: Any, red: Any, valid_mask: Any | None = None) -> np.ndarray:
    """Return NDVI; invalid pixels and zero denominators are NaN."""
    nir_arr = _as_2d("nir", nir).astype(float)
    red_arr = _as_2d("red", red).astype(float)
    if nir_arr.shape != red_arr.shape:
        raise ValueError("NIR and red arrays must have matching dimensions")
    mask = np.ones(nir_arr.shape, dtype=bool) if valid_mask is None else _as_2d(
        "valid_mask", valid_mask
    ).astype(bool)
    if mask.shape != nir_arr.shape:
        raise ValueError("valid_mask dimensions must match bands")
    denominator = nir_arr + red_arr
    usable = mask & np.isfinite(nir_arr) & np.isfinite(red_arr) & (denominator != 0)
    result = np.full(nir_arr.shape, np.nan, dtype=float)
    np.divide(nir_arr - red_arr, denominator, out=result, where=usable)
    return result


def compare_scenes(scene: dict[str, Any], decline_threshold: float = -0.10) -> ComparisonResult:
    """Compare two dates only on farm pixels valid on both dates."""
    required = [
        "red_before", "nir_before", "red_after", "nir_after",
        "valid_before", "valid_after", "farm_mask", "pixel_size_m",
    ]
    missing = [key for key in required if key not in scene]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    arrays = {key: _as_2d(key, scene[key]) for key in required[:-1]}
    shapes = {arr.shape for arr in arrays.values()}
    if len(shapes) != 1:
        raise ValueError("All band, mask, and farm arrays must have matching dimensions")

    farm = np.asarray(scene["farm_mask"], dtype=bool)
    valid_before = np.asarray(scene["valid_before"], dtype=bool)
    valid_after = np.asarray(scene["valid_after"], dtype=bool)
    before = calculate_ndvi(scene["nir_before"], scene["red_before"], valid_before)
    after = calculate_ndvi(scene["nir_after"], scene["red_after"], valid_after)
    shared = farm & valid_before & valid_after & np.isfinite(before) & np.isfinite(after)
    delta = np.full(before.shape, np.nan, dtype=float)
    delta[shared] = after[shared] - before[shared]

    farm_count = int(farm.sum())
    shared_count = int(shared.sum())
    before_farm_valid = farm & np.isfinite(before) & valid_before
    after_farm_valid = farm & np.isfinite(after) & valid_after

    def mean_or_none(values: np.ndarray, mask: np.ndarray) -> float | None:
        return float(np.mean(values[mask])) if np.any(mask) else None

    pixel_size = scene["pixel_size_m"]
    if not isinstance(pixel_size, (list, tuple)) or len(pixel_size) != 2:
        raise ValueError("pixel_size_m must be [pixel_width_m, pixel_height_m]")
    pixel_width, pixel_height = map(float, pixel_size)
    if pixel_width <= 0 or pixel_height <= 0:
        raise ValueError("Pixel dimensions must be positive")

    before_mean = mean_or_none(before, shared)
    after_mean = mean_or_none(after, shared)
    mean_change = mean_or_none(delta, shared)
    summary = {
        "data_origin": scene.get("metadata", {}).get("origin", "unspecified"),
        "comparison_method": "NDVI; same farm pixels valid on both dates",
        "decline_threshold": float(decline_threshold),
        "before": {
            "mean_ndvi_shared_pixels": before_mean,
            "valid_farm_pixels": int(before_farm_valid.sum()),
            "valid_farm_coverage_percent": round(100 * before_farm_valid.sum() / farm_count, 2) if farm_count else 0.0,
        },
        "after": {
            "mean_ndvi_shared_pixels": after_mean,
            "valid_farm_pixels": int(after_farm_valid.sum()),
            "valid_farm_coverage_percent": round(100 * after_farm_valid.sum() / farm_count, 2) if farm_count else 0.0,
        },
        "comparison": {
            "farm_pixel_count": farm_count,
            "usable_shared_pixel_count": shared_count,
            "usable_shared_pixel_percent_of_farm": round(100 * shared_count / farm_count, 2) if farm_count else 0.0,
            "mean_ndvi_change_after_minus_before": mean_change,
            "decline_flag": bool(mean_change is not None and mean_change <= decline_threshold),
            "changed_pixel_count_decline": int(np.sum(delta[shared] <= decline_threshold)),
            "pixel_area_m2": pixel_width * pixel_height,
        },
        "interpretation_warning": (
            "An NDVI decline alone does not establish disease, cause, or yield loss. "
            "Clouds, seasonal differences, illumination, atmosphere, and sensor differences may affect results."
        ),
    }
    return ComparisonResult(summary, before, after, delta, shared)
