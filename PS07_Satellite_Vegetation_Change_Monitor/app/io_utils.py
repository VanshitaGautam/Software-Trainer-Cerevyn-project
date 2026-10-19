"""Scene loading and portable result exports."""
import csv
import io
import json
from pathlib import Path
from typing import Any


def load_scene(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def to_json_bytes(summary: dict[str, Any]) -> bytes:
    return json.dumps(summary, indent=2, allow_nan=False).encode("utf-8")


def to_csv_bytes(summary: dict[str, Any]) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["metric", "value"])
    writer.writerow(["before_mean_ndvi_shared_pixels", summary["before"]["mean_ndvi_shared_pixels"]])
    writer.writerow(["after_mean_ndvi_shared_pixels", summary["after"]["mean_ndvi_shared_pixels"]])
    writer.writerow(["mean_ndvi_change", summary["comparison"]["mean_ndvi_change_after_minus_before"]])
    writer.writerow(["usable_shared_pixel_count", summary["comparison"]["usable_shared_pixel_count"]])
    writer.writerow(["usable_shared_pixel_percent_of_farm", summary["comparison"]["usable_shared_pixel_percent_of_farm"]])
    writer.writerow(["decline_flag", summary["comparison"]["decline_flag"]])
    return output.getvalue().encode("utf-8")
