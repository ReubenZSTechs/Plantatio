"""Reference land-cover tiles used for the map legend.

These come from `misc/eurosat_vlm_labels.jsonl`, which was produced by
prompting a vision model that had already been told each tile's class. The
labels are therefore illustrative, not ground truth, and they carry no
coordinates — so they populate the legend and tests, and nothing is placed on
the map from them.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

REFERENCE_PATH = Path(__file__).resolve().parents[2] / "misc" / "eurosat_vlm_labels.jsonl"


@lru_cache(maxsize=1)
def load_reference_tiles() -> list[dict]:
    """Read the labelled reference tiles, normalising their image paths."""
    if not REFERENCE_PATH.is_file():
        return []

    tiles: list[dict] = []
    for line in REFERENCE_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Paths were written on Windows and carry backslash separators.
        record["image_path"] = record.get("image_path", "").replace("\\", "/")
        tiles.append(record)

    return tiles


@lru_cache(maxsize=1)
def reference_tile_counts() -> dict[str, int]:
    """Number of reference tiles per land-cover class."""
    counts: dict[str, int] = {}
    for tile in load_reference_tiles():
        name = tile.get("class_name", "")
        counts[name] = counts.get(name, 0) + 1
    return counts
