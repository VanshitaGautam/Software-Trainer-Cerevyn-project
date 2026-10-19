# PS07 — Satellite Vegetation Change Monitor

A reproducible, local-first prototype for comparing vegetation between two dates using synthetic red and near-infrared (NIR) satellite-band arrays. Built for the Cerevyn Chitkara Software Developer Trainee assessment.

> **Data note:** Included arrays are synthetic teaching data, not real satellite observations. A falling NDVI can indicate a change in vegetation greenness, but does not establish disease, cause, or yield loss.

## Features
- Calculates NDVI: `(NIR - Red) / (NIR + Red)`.
- Treats zero denominators and invalid/cloud-masked pixels as invalid (`NaN` internally), never as vegetation values.
- Compares both dates on the *same* farm pixels that are valid on both dates.
- Reports date means, mean change, usable-pixel count/percentage and configurable decline flag.
- Generates grayscale heatmaps and downloadable CSV/JSON results.
- Includes synthetic sample arrays, automated tests, GitHub Actions CI, Docker packaging, and an Azure deployment plan.

## Quick start (Python 3.11 recommended)
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```
Open the local URL shown by Streamlit (usually `http://localhost:8501`).

## Run tests
```bash
pip install -r requirements-dev.txt
pytest -q
```

## Run without the dashboard
```bash
python -m app.cli --data sample_data/sample_scene.json --threshold -0.10
```
The command writes `results.json`, `ndvi_before.png`, and `ndvi_after.png` to the current directory.

## Input format
JSON object with:
- `red_before`, `nir_before`, `red_after`, `nir_after`: rectangular numeric arrays, same dimensions.
- `valid_before`, `valid_after`: rectangular boolean masks (`true` means valid).
- `farm_mask`: rectangular boolean mask (`true` means farm area).
- `pixel_size_m`: pixel width and height in metres, e.g. `[10, 10]`.
- `metadata`: origin / alignment description.

All arrays must have identical dimensions. The example data is synthetic. For a real dataset, ensure scenes are co-registered, use comparable reflectance products and provide cloud/quality masks.

## Interpretation
NDVI ranges approximately from -1 to +1. Higher values commonly correspond to greener vegetation, but water, soil, season, atmosphere, illumination and sensor differences can affect it. This baseline reports measurements; it does not infer the cause of a change.

## Project layout
- `app/ndvi.py` — calculation and comparison logic
- `app/visuals.py` — grayscale heatmap generation
- `app/cli.py` — command-line runner
- `app/streamlit_app.py` — interactive dashboard and downloads
- `sample_data/sample_scene.json` — reproducible 10×10 synthetic scene
- `tests/` — unit and workflow tests
- `docs/azure-plan.md` — deployment design
- `.github/workflows/ci.yml` — test automation
- `Dockerfile` — container setup

## Azure deployment plan
See [`docs/azure-plan.md`](docs/azure-plan.md). Live deployment is optional for the assessment.
