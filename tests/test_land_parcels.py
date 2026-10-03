"""Restoration-candidate parcels, their scoring, and the land-cover legend."""

import pytest

from backend.services.land_reference import load_reference_tiles, reference_tile_counts
from backend.services.land_service import (
    polygon_area_hectares, polygon_centroid, restoration_potential, square_around,
)


def test_degraded_land_outranks_mature_forest():
    """Restoration potential measures headroom, not current ecological value."""
    pasture = restoration_potential("Pasture", canopy_cover=0.08, confidence=0.9)
    forest = restoration_potential("Forest", canopy_cover=0.88, confidence=0.9)

    assert pasture.value > forest.value


def test_built_land_scores_near_zero():
    for land_cover in ("Residential", "Industrial", "Highway"):
        score = restoration_potential(land_cover, canopy_cover=0.0, confidence=0.9)
        assert score.value < 0.15, land_cover


def test_score_is_monotonic_in_missing_canopy():
    """Less existing canopy means more to restore."""
    scores = [
        restoration_potential("Pasture", canopy_cover=cover, confidence=0.9).value
        for cover in (0.0, 0.25, 0.5, 0.75, 1.0)
    ]

    assert scores == sorted(scores, reverse=True)


def test_low_confidence_is_discounted():
    confident = restoration_potential("Pasture", 0.1, confidence=1.0)
    unsure = restoration_potential("Pasture", 0.1, confidence=0.0)

    assert confident.value > unsure.value


def test_score_stays_within_bounds():
    assert restoration_potential("Pasture", -5, 5).value <= 1.0
    assert restoration_potential("Unknown", None, None).value >= 0.0


def test_geometry_helpers_agree_with_their_input():
    geometry = square_around(-6.1754, 106.8272, 800)
    ring = geometry["coordinates"][0]

    # An 800 m square is 64 hectares.
    assert polygon_area_hectares(ring) == pytest.approx(64.0, rel=0.02)

    latitude, longitude = polygon_centroid(ring)
    assert latitude == pytest.approx(-6.1754, abs=1e-4)
    assert longitude == pytest.approx(106.8272, abs=1e-4)


def test_parcels_are_seeded_and_ranked(client):
    response = client.get("/api/b2b/land-parcels")

    assert response.status_code == 200
    parcels = response.json()
    assert len(parcels) >= 6

    scores = [p["restorationPotential"] for p in parcels]
    assert scores == sorted(scores, reverse=True)

    # Every parcel is an area with real coordinates, not a bare point.
    for parcel in parcels:
        assert parcel["geometry"]["type"] == "Polygon"
        assert parcel["areaHectares"] > 0
        assert -90 <= parcel["centroidLatitude"] <= 90
        assert -180 <= parcel["centroidLongitude"] <= 180
        assert parcel["rationale"]


def test_parcels_can_be_filtered(client):
    filtered = client.get("/api/b2b/land-parcels?min_potential=0.5").json()

    assert filtered
    assert all(p["restorationPotential"] >= 0.5 for p in filtered)

    pasture = client.get("/api/b2b/land-parcels?land_cover_class=Pasture").json()
    assert all(p["landCoverClass"] == "Pasture" for p in pasture)


def test_drawing_a_parcel_scores_it(client):
    response = client.post(
        "/api/b2b/land-parcels",
        json={
            "name": "New Candidate",
            "zone": "Sektor D",
            "landCoverClass": "Pasture",
            "canopyCover": 0.1,
            "confidence": 0.8,
            "geometry": square_around(-6.18, 106.83, 600),
        },
    )

    assert response.status_code == 201, response.text
    parcel = response.json()
    assert parcel["restorationPotential"] > 0.5
    assert parcel["areaHectares"] == pytest.approx(36.0, rel=0.05)


def test_invalid_geometry_is_rejected(client):
    response = client.post(
        "/api/b2b/land-parcels",
        json={"name": "Bad", "geometry": {"type": "Point", "coordinates": [1, 2]}},
    )

    assert response.status_code == 422


def test_reference_tiles_are_labelled_but_carry_no_coordinates(client):
    """The EuroSAT corpus supplies the legend only; nothing is mapped from it."""
    tiles = load_reference_tiles()

    assert len(tiles) == 45
    assert reference_tile_counts()["Forest"] == 5
    # Windows separators are normalised on load.
    assert all("\\" not in tile["image_path"] for tile in tiles)
    # This is why these cannot be placed on the map.
    assert all("lat" not in tile and "lon" not in tile for tile in tiles)

    legend = client.get("/api/b2b/land-cover-classes").json()
    assert {entry["name"] for entry in legend} >= {"Forest", "Pasture", "Residential"}
    assert legend == sorted(legend, key=lambda e: -e["headroom"])
