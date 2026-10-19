import json
from pathlib import Path
import numpy as np
import pytest
from app.ndvi import calculate_ndvi, compare_scenes
from app.io_utils import load_scene

ROOT = Path(__file__).resolve().parents[1]


def test_required_example_ndvi_is_point_five():
    assert calculate_ndvi([[0.6]], [[0.2]])[0, 0] == pytest.approx(0.5)


def test_zero_denominator_is_invalid():
    assert np.isnan(calculate_ndvi([[0.0]], [[0.0]])[0, 0])


def test_masked_pixel_is_invalid():
    assert np.isnan(calculate_ndvi([[0.6]], [[0.2]], [[False]])[0, 0])


def test_rejects_mismatched_band_dimensions():
    with pytest.raises(ValueError, match="matching dimensions"):
        calculate_ndvi([[0.6, 0.7]], [[0.2]])


def test_comparison_uses_shared_farm_pixels_only():
    scene = {
        "red_before": [[0.2, 0.2], [0.2, 0.2]],
        "nir_before": [[0.6, 0.6], [0.6, 0.6]],
        "red_after": [[0.2, 0.2], [0.2, 0.2]],
        "nir_after": [[0.4, 0.4], [0.4, 0.4]],
        "valid_before": [[True, True], [True, True]],
        "valid_after": [[True, False], [True, True]],
        "farm_mask": [[True, True], [False, True]],
        "pixel_size_m": [10, 10],
    }
    result = compare_scenes(scene)
    assert result.summary["comparison"]["usable_shared_pixel_count"] == 2
    assert result.summary["comparison"]["farm_pixel_count"] == 3


def test_sample_data_is_10_by_10_and_declares_synthetic_origin():
    scene = load_scene(ROOT / "sample_data" / "sample_scene.json")
    assert len(scene["red_before"]) == 10
    assert len(scene["red_before"][0]) == 10
    assert "synthetic" in scene["metadata"]["origin"].lower()
    assert compare_scenes(scene).summary["comparison"]["usable_shared_pixel_count"] > 0


def test_empty_shared_area_has_no_mean_not_zero():
    scene = {
        "red_before": [[0.2]], "nir_before": [[0.6]],
        "red_after": [[0.2]], "nir_after": [[0.6]],
        "valid_before": [[False]], "valid_after": [[False]],
        "farm_mask": [[True]], "pixel_size_m": [10, 10],
    }
    result = compare_scenes(scene)
    assert result.summary["comparison"]["usable_shared_pixel_count"] == 0
    assert result.summary["comparison"]["mean_ndvi_change_after_minus_before"] is None
