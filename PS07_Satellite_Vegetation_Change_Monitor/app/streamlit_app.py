"""Streamlit dashboard for the PS07 prototype."""
from pathlib import Path
import json
import streamlit as st
import numpy as np
from app.io_utils import load_scene, to_csv_bytes, to_json_bytes
from app.ndvi import compare_scenes
from app.visuals import heatmap_png

ROOT = Path(__file__).resolve().parents[1]
st.set_page_config(page_title="Vegetation Change Monitor", page_icon="🌱", layout="wide")
st.title("🌱 Satellite Vegetation Change Monitor")
st.caption("PS07 • NDVI comparison across two dates • synthetic demonstration data")

with st.sidebar:
    st.header("Analysis settings")
    threshold = st.slider("Decline threshold", min_value=-1.0, max_value=0.0, value=-0.10, step=0.05)
    uploaded = st.file_uploader("Optional scene JSON", type=["json"])
    st.info("Included scene is synthetic. Real imagery must be aligned and use comparable reflectance products.")

try:
    scene = json.load(uploaded) if uploaded else load_scene(ROOT / "sample_data" / "sample_scene.json")
    result = compare_scenes(scene, threshold)
except Exception as exc:
    st.error(f"Could not analyse this scene: {exc}")
    st.stop()

summary = result.summary
c1, c2, c3, c4 = st.columns(4)
c1.metric("Before mean NDVI", "N/A" if summary["before"]["mean_ndvi_shared_pixels"] is None else f'{summary["before"]["mean_ndvi_shared_pixels"]:.3f}')
c2.metric("After mean NDVI", "N/A" if summary["after"]["mean_ndvi_shared_pixels"] is None else f'{summary["after"]["mean_ndvi_shared_pixels"]:.3f}')
change = summary["comparison"]["mean_ndvi_change_after_minus_before"]
c3.metric("Mean change", "N/A" if change is None else f"{change:+.3f}")
c4.metric("Shared valid pixels", f'{summary["comparison"]["usable_shared_pixel_count"]} / {summary["comparison"]["farm_pixel_count"]}')

if summary["comparison"]["decline_flag"]:
    st.warning(f"Decline threshold reached (change ≤ {threshold:.2f}). This is a measurement flag, not a diagnosis.")
else:
    st.success("Configured decline threshold was not reached, or no shared valid pixels were available.")

left, right = st.columns(2)
with left:
    st.subheader("Before date — NDVI")
    st.image(heatmap_png(result.ndvi_before, "NDVI before"), use_container_width=True)
    st.caption(f'Valid farm coverage: {summary["before"]["valid_farm_coverage_percent"]}%')
with right:
    st.subheader("After date — NDVI")
    st.image(heatmap_png(result.ndvi_after, "NDVI after"), use_container_width=True)
    st.caption(f'Valid farm coverage: {summary["after"]["valid_farm_coverage_percent"]}%')

st.subheader("Pixel change (after − before)")
st.image(heatmap_png(result.delta, "NDVI change", vmin=-1, vmax=1), use_container_width=True)
st.caption("Only farm pixels valid on both dates contribute to the comparison. Gray levels are visual only; use exported numeric values for analysis.")
st.subheader("Summary")
st.json(summary)
st.download_button("Download results.json", data=to_json_bytes(summary), file_name="vegetation_change_results.json", mime="application/json")
st.download_button("Download summary.csv", data=to_csv_bytes(summary), file_name="vegetation_change_summary.csv", mime="text/csv")

with st.expander("Method and limitations"):
    st.markdown("""
    - NDVI = (NIR − Red) / (NIR + Red).
    - Zero denominators, cloud masks and invalid values are excluded.
    - Means and pixel changes use the same farm pixels valid at both dates.
    - NDVI decline alone does not establish disease, cause or yield loss.
    - Different illumination, seasons, atmosphere, sensors or misalignment can create misleading changes.
    """)
