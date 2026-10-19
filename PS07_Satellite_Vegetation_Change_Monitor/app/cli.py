"""CLI for reproducible sample-scene comparison."""
import argparse
import json
from pathlib import Path
from app.io_utils import load_scene
from app.ndvi import compare_scenes
from app.visuals import heatmap_png


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare vegetation NDVI between two dates.")
    parser.add_argument("--data", default="sample_data/sample_scene.json")
    parser.add_argument("--threshold", type=float, default=-0.10, help="NDVI decline threshold (default: -0.10)")
    parser.add_argument("--out", default=".")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    result = compare_scenes(load_scene(args.data), args.threshold)
    (out / "results.json").write_text(json.dumps(result.summary, indent=2), encoding="utf-8")
    (out / "ndvi_before.png").write_bytes(heatmap_png(result.ndvi_before, "NDVI — before"))
    (out / "ndvi_after.png").write_bytes(heatmap_png(result.ndvi_after, "NDVI — after"))
    print(json.dumps(result.summary, indent=2))


if __name__ == "__main__":
    main()
