"""Grayscale heatmaps for NDVI and pixel change."""
from __future__ import annotations
import io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def heatmap_png(values: np.ndarray, title: str, vmin: float = -1.0, vmax: float = 1.0) -> bytes:
    fig, ax = plt.subplots(figsize=(5, 4))
    image = ax.imshow(values, cmap="gray", vmin=vmin, vmax=vmax, interpolation="nearest")
    ax.set_title(title)
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=130)
    plt.close(fig)
    return buffer.getvalue()
