"""The satellite response contract, which silently lost data in three ways."""

from app.schema import EuroSatAnalysisResponse, MLLabels


def test_restoration_delta_survives_serialisation():
    """MLLabels had no delta field, so pydantic dropped the before/after
    comparison the endpoint exists to compute."""
    response = EuroSatAnalysisResponse(
        image_path="current.png",
        class_name="Satellite Restoration Analysis",
        labels={
            "canopy_cover": 0.8,
            "restoration_delta": {"canopy_cover_change": 0.45},
        },
    )

    payload = response.model_dump(by_alias=True)
    assert payload["labels"]["restorationDelta"]["canopyCoverChange"] == 0.45


def test_carbon_field_uses_the_key_the_frontend_reads():
    """Field(alias="carbon_EQ") overrode the camelCase generator, so the UI's
    `carbonEq` lookup was always undefined and the tile rendered blank."""
    payload = MLLabels(carbon_eq=3.2).model_dump(by_alias=True)

    assert "carbonEq" in payload
    assert payload["carbonEq"] == 3.2
    assert "carbon_EQ" not in payload


def test_missing_metrics_do_not_raise():
    """Every field was required but fed .get() results, so one omitted key
    from the vision model produced an uncatchable 500."""
    labels = MLLabels()

    assert labels.confidence is None
    assert labels.vegetation_density is None


def test_partial_delta_is_allowed():
    labels = MLLabels(restoration_delta={"canopy_cover_change": 0.1})

    assert labels.restoration_delta.canopy_cover_change == 0.1
    assert labels.restoration_delta.biomass_change is None
