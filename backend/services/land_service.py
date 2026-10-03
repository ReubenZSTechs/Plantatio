"""Scoring and seeding for restoration land parcels.

A parcel's restoration potential answers a different question from its current
ecological value: degraded land with room to recover scores high, while mature
forest scores low because there is little left to restore. Built land scores
near zero because it is not available.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass

# How much headroom each land cover offers, and how available it is for
# restoration work. Derived from the EuroSAT classes the corpus uses.
LAND_COVER_PROFILE: dict[str, tuple[float, str]] = {
    "Pasture": (0.90, "Grazing land; high recovery headroom with low conflict."),
    "HerbaceousVegetation": (0.85, "Scrub and grassland; readily reforested."),
    "AnnualCrop": (0.65, "Rotational cropland; agroforestry is viable."),
    "PermanentCrop": (0.45, "Established plantation; partial interplanting only."),
    "River": (0.40, "Riparian margin; buffer planting only."),
    "Forest": (0.15, "Already closed canopy; conserve rather than restore."),
    "Highway": (0.10, "Transport corridor; verge planting at best."),
    "Residential": (0.05, "Built land; not available for restoration."),
    "Industrial": (0.05, "Built land; not available for restoration."),
}

DEFAULT_PROFILE = (0.30, "Unclassified land cover.")


@dataclass(frozen=True)
class PotentialScore:
    """A parcel's restoration potential and why it scored that way."""

    value: float
    rationale: str


def restoration_potential(land_cover_class: str, canopy_cover: float | None,
                          confidence: float | None = None) -> PotentialScore:
    """Score a parcel's restoration potential between 0 and 1.

    Combines how much headroom the land cover allows with how much of the
    canopy is currently missing, then scales by the model's confidence.

    Args:
        land_cover_class: EuroSAT-style land-cover label.
        canopy_cover: Current canopy fraction, 0-1.
        confidence: Model confidence in the assessment, 0-1.

    Returns:
        The score and a short human-readable rationale.
    """
    headroom, note = LAND_COVER_PROFILE.get(land_cover_class, DEFAULT_PROFILE)

    cover = 0.0 if canopy_cover is None else min(max(canopy_cover, 0.0), 1.0)
    missing_canopy = 1.0 - cover

    score = headroom * missing_canopy

    # A low-confidence assessment should not rank above a confident one.
    if confidence is not None:
        score *= 0.5 + 0.5 * min(max(confidence, 0.0), 1.0)

    return PotentialScore(round(min(max(score, 0.0), 1.0), 3), note)


def polygon_centroid(coordinates: list[list[float]]) -> tuple[float, float]:
    """Return the (latitude, longitude) centroid of a GeoJSON ring."""
    ring = coordinates[:-1] if coordinates[0] == coordinates[-1] else coordinates
    longitude = sum(point[0] for point in ring) / len(ring)
    latitude = sum(point[1] for point in ring) / len(ring)
    return latitude, longitude


def polygon_area_hectares(coordinates: list[list[float]]) -> float:
    """Approximate a small GeoJSON ring's area in hectares.

    Uses an equirectangular projection about the ring's centroid, which is
    accurate enough for parcels of a few square kilometres.
    """
    ring = coordinates[:-1] if coordinates[0] == coordinates[-1] else coordinates
    latitude, _ = polygon_centroid(coordinates)

    metres_per_degree_lat = 111_132.0
    metres_per_degree_lon = 111_320.0 * math.cos(math.radians(latitude))

    points = [
        (point[0] * metres_per_degree_lon, point[1] * metres_per_degree_lat)
        for point in ring
    ]

    # Shoelace formula.
    area = 0.0
    for index, (x1, y1) in enumerate(points):
        x2, y2 = points[(index + 1) % len(points)]
        area += x1 * y2 - x2 * y1

    return round(abs(area) / 2.0 / 10_000.0, 3)


def square_around(latitude: float, longitude: float, metres: float) -> dict:
    """Build a square GeoJSON polygon centred on a point."""
    half_lat = (metres / 2) / 111_132.0
    half_lon = (metres / 2) / (111_320.0 * math.cos(math.radians(latitude)) or 1.0)

    ring = [
        [longitude - half_lon, latitude - half_lat],
        [longitude + half_lon, latitude - half_lat],
        [longitude + half_lon, latitude + half_lat],
        [longitude - half_lon, latitude + half_lat],
        [longitude - half_lon, latitude - half_lat],
    ]

    return {"type": "Polygon", "coordinates": [ring]}


def geometry_to_json(geometry: dict) -> str:
    """Serialise a GeoJSON geometry for storage."""
    return json.dumps(geometry, separators=(",", ":"))
