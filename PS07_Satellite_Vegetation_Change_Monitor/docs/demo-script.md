# 3–5 minute demo script

1. **Problem (20 sec):** Compare vegetation index across two dates while handling invalid/cloud-masked pixels.
2. **Run (30 sec):** `pip install -r requirements.txt` then `streamlit run app/streamlit_app.py`.
3. **Results (60 sec):** Explain before/after means, shared valid pixel count and decline threshold.
4. **Exports (30 sec):** Download JSON and CSV. Point out the synthetic data label.
5. **Correctness (60 sec):** Run `pytest -q`; explain NDVI 0.5 for NIR 0.6 and Red 0.2, zero-denominator masking and common-pixel comparison.
6. **Engineering (60 sec):** Walk through module separation, CI workflow, Dockerfile and Azure plan.
7. **Limitations (20 sec):** Decline does not identify cause; cloud, season, lighting and alignment can affect results.
