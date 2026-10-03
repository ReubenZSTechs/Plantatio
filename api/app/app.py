"""HTTP surface for Plantatio: plants, telemetry, devices and the AI agent."""

import datetime
import io
import json
import logging
import os
import random
import tempfile
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from .db import (
    ChatLog, IotNodeDB, PlantDB, ProbeDataDB, ScannedItemDB, TacticalLogDB,
    DiagnosisLogDB, LandParcelDB, SatelliteAnalysisLogDB, TimelineEventDB,
    WeatherLog, create_tables, get_db, init_seed_data,
)
from .schema import (
    ChatRequest, ChatResponse, DiagnosisResponse, EuroSatAnalysisResponse,
    GraphProvenance,
    IotNode, IotNodeCreate, LandCoverClass, LandParcel, LandParcelCreate, Plant,
    PlantCreate, SatelliteAnalysis, ScannedItem, TacticalLog,
    WeatherAlertResponse, WeatherMacroResponse,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Prepare the database on startup and release model resources on shutdown."""
    create_tables()
    init_seed_data()
    yield

    from backend.pipelines.main.nodes.nodes import close_retrieval_pipeline

    close_retrieval_pipeline()


app = FastAPI(title="Plantatio API", lifespan=lifespan)

# Credentials are not used by this API, so a wildcard origin would be rejected
# by browsers anyway; the allowed origins come from configuration instead.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Weather Endpoints (Dari script asli Anda) ──────────────────────────────────

@app.get("/api/v1/weather/macro", response_model=WeatherMacroResponse)
async def get_weather_macro(db: Session = Depends(get_db)):
    new_log = WeatherLog(
        city="Restoration Zone, Jakarta",
        tempC=32.0,
        condition="Partly cloudy"
    )
    db.add(new_log)
    db.commit()

    # Menggunakan temp_c sesuai properti Pydantic (diubah otomatis ke tempC oleh CamelModel di schema)
    return WeatherMacroResponse(
        city="Restoration Zone, Jakarta",
        temp_c=32,
        condition="Partly cloudy",
        humidity=65,
        forecast=[
            {"day": "Mon", "icon": "sun", "temp_c": 33},
            {"day": "Tue", "icon": "cloud", "temp_c": 31},
            {"day": "Wed", "icon": "rain", "temp_c": 28},
            {"day": "Thu", "icon": "rain", "temp_c": 27},
            {"day": "Fri", "icon": "cloud", "temp_c": 30},
        ]
    )

@app.get("/api/v1/weather/alert", response_model=WeatherAlertResponse)
async def get_weather_alert():
    return WeatherAlertResponse(
        title="Heat stress warning",
        body="Macro temperature is above the adaptation threshold for young plants. Consider deploying shade cover."
    )

# ── Chat ──────────────────────────────────────────────────────────────────────

def _run_agent(user_text: str) -> dict:
    """Invoke the GraphRAG agent for one question.

    Imported lazily so that a missing model backend degrades this one endpoint
    instead of preventing the whole API from starting.
    """
    from backend.pipelines.main.nodes.nodes import get_graph_app

    return get_graph_app().invoke({"user_query": user_text})


def _build_provenance(result: dict) -> GraphProvenance:
    """Summarise what the agent retrieved, for display alongside the answer."""
    records = result.get("graph_records") or []
    facts = result.get("retrieved_docs") or []

    return GraphProvenance(
        sub_questions=result.get("sub_questions") or [],
        retrieved_facts=facts[:8],
        record_count=len(records),
        graph_available=bool(records),
    )


def _build_tags(result: dict) -> List[str]:
    """Describe which capabilities actually contributed to this answer."""
    tags: List[str] = []

    if result.get("graph_records"):
        tags.append("Knowledge Graph")
    if result.get("sub_questions"):
        tags.append("Query Decomposition")
    if result.get("reasoning_output"):
        tags.append("Step-by-step Reasoning")

    return tags or ["Direct Answer"]


async def _handle_chat(request: ChatRequest, plant_id: Optional[int], db: Session) -> ChatResponse:
    """Answer a chat turn and record it against the plant it concerns."""
    if not request.messages:
        raise HTTPException(status_code=422, detail="messages must not be empty")

    # Casing is preserved: lower-casing here used to destroy proper nouns and
    # units before they ever reached the model.
    user_text = request.messages[-1].content.strip()
    if not user_text:
        raise HTTPException(status_code=422, detail="The last message is empty")

    try:
        result = await run_in_threadpool(_run_agent, user_text)
    except Exception as exc:
        logger.exception("Agent invocation failed.")
        raise HTTPException(
            status_code=503,
            detail=f"The assistant is unavailable: {exc}",
        ) from exc

    answer = (result or {}).get("final_answer")
    if not answer:
        raise HTTPException(
            status_code=502,
            detail="The assistant did not produce an answer.",
        )

    resolved_plant_id = plant_id if plant_id is not None else request.plant_id

    db.add(ChatLog(
        plant_id=resolved_plant_id,
        user_message=user_text,
        bot_response=answer,
    ))
    db.commit()

    return ChatResponse(
        role="assistant",
        text=answer,
        tags=_build_tags(result),
        provenance=_build_provenance(result),
    )


@app.post("/api/b2c/chat", response_model=ChatResponse)
async def chat_b2c(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """General growing question from a consumer, not tied to one plant."""
    return await _handle_chat(request, None, db)


@app.post("/api/b2b/chat", response_model=ChatResponse)
async def chat_b2b(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """Operational question from an enterprise user."""
    return await _handle_chat(request, None, db)


@app.post("/api/plants/{plant_id}/chat", response_model=ChatResponse)
async def chat_about_plant(
    plant_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """Question about one specific plant in the user's garden."""
    return await _handle_chat(request, plant_id, db)


# ── Plant Endpoints (Dibutuhkan Frontend) ──────────────────────────────────────

@app.get("/api/plants/{plant_id}", response_model=Plant)
async def get_plant(plant_id: int, db: Session = Depends(get_db)):
    plant = db.query(PlantDB).filter(PlantDB.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant

@app.post("/api/plants/{plant_id}/scan", response_model=Plant)
async def scan_item(plant_id: int, item: ScannedItem, db: Session = Depends(get_db)):
    plant = db.query(PlantDB).filter(PlantDB.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    # Replace any previous item in the same category so a plant does not
    # accumulate duplicate sensors or seed records.
    db.query(ScannedItemDB).filter(
        ScannedItemDB.plant_id == plant_id, 
        ScannedItemDB.category == item.category
    ).delete()
    
    new_item = ScannedItemDB(
        id=item.id,
        plant_id=plant_id,
        category=item.category,
        name=item.name,
        brand=item.brand,
        sensor_id=item.sensor_id,
        seed_variety=item.seed_variety,
        germination_days=item.germination_days,
        soil_type=item.soil_type,
        ph_level=item.ph_level,
        npk_ratio=item.npk_ratio,
        application_frequency=item.application_frequency,
        description=item.description,
        scanned_at=item.scanned_at
    )
    db.add(new_item)

    # A scanned sensor brings the probe readings online.
    if item.category == "sensor" and plant.probe:
        plant.probe.moisture = 72.0
        plant.probe.nutrients = 68.0
        plant.probe.light = 85.0
        plant.probe.temperature = 24.0

    event_labels = {
        "sensor": "Sensor installed", "seed": "Seed confirmed", 
        "soil": "Growing medium changed", "fertilizer": "Fertiliser applied", "other": "Context updated"
    }
    today = datetime.datetime.now().strftime("%d %b")
    
    new_timeline = TimelineEventDB(
        plant_id=plant_id,
        date=today,
        event=event_labels.get(item.category, "Item added"),
        note=f"{item.name} ({item.brand or ''}) synced",
        scan_category=item.category
    )
    db.add(new_timeline)

    db.commit()
    db.refresh(plant)
    
    return plant

@app.get("/api/plants", response_model=List[Plant])
async def get_all_plants(db: Session = Depends(get_db)):
    plants = db.query(PlantDB).all()
    return plants

@app.post("/api/plants", response_model=Plant)
async def create_plant(plant_req: PlantCreate, db: Session = Depends(get_db)):
    new_plant = PlantDB(
        nickname=plant_req.nickname,
        species=plant_req.species,
        image=plant_req.image,
        health=100.0,
        days_planted=1
    )
    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)

    # Every plant starts with a probe so the UI has readings to show.
    default_probe = ProbeDataDB(
        plant_id=new_plant.id,
        moisture=50.0, nutrients=50.0, light=50.0, temperature=24.0
    )
    db.add(default_probe)

    today = datetime.datetime.now().strftime("%d %b")
    creation_timeline = TimelineEventDB(
        plant_id=new_plant.id,
        date=today,
        event="Registered",
        note="Added via the Plantatio scanner"
    )
    db.add(creation_timeline)
    
    db.commit()
    db.refresh(new_plant)
    
    return new_plant

@app.delete("/api/plants/{plant_id}")
async def delete_plant(plant_id: int, db: Session = Depends(get_db)):
    plant = db.query(PlantDB).filter(PlantDB.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    db.delete(plant)
    db.commit()
    return {"message": "Plant deleted"}

# ── Land parcels ──────────────────────────────────────────────────────────────

def _parcel_to_schema(row: LandParcelDB) -> LandParcel:
    """Convert a stored parcel into its API shape, decoding the geometry."""
    from backend.services.land_service import LAND_COVER_PROFILE, DEFAULT_PROFILE

    _, rationale = LAND_COVER_PROFILE.get(row.land_cover_class or "", DEFAULT_PROFILE)

    return LandParcel(
        id=row.id,
        name=row.name,
        zone=row.zone,
        geometry=json.loads(row.geometry),
        centroid_latitude=row.centroid_latitude,
        centroid_longitude=row.centroid_longitude,
        area_hectares=row.area_hectares,
        land_cover_class=row.land_cover_class,
        vegetation_density=row.vegetation_density,
        canopy_cover=row.canopy_cover,
        est_biomass=row.est_biomass,
        carbon_eq=row.carbon_eq,
        restoration_quality=row.restoration_quality,
        confidence=row.confidence,
        restoration_potential=row.restoration_potential,
        rationale=rationale,
        analyzed_at=row.analyzed_at,
    )


@app.get("/api/b2b/land-parcels", response_model=List[LandParcel])
async def list_land_parcels(
    min_potential: float = 0.0,
    land_cover_class: Optional[str] = None,
    db: Session = Depends(get_db),
) -> List[LandParcel]:
    """Restoration candidates, highest potential first."""
    query = db.query(LandParcelDB)

    if min_potential > 0:
        query = query.filter(LandParcelDB.restoration_potential >= min_potential)
    if land_cover_class:
        query = query.filter(LandParcelDB.land_cover_class == land_cover_class)

    rows = query.order_by(LandParcelDB.restoration_potential.desc()).all()
    return [_parcel_to_schema(row) for row in rows]


@app.post("/api/b2b/land-parcels", response_model=LandParcel, status_code=201)
async def create_land_parcel(
    parcel: LandParcelCreate,
    db: Session = Depends(get_db),
) -> LandParcel:
    """Register a parcel drawn on the map, scoring it on the way in."""
    from backend.services.land_service import (
        geometry_to_json, polygon_area_hectares, polygon_centroid,
        restoration_potential,
    )

    coordinates = (parcel.geometry or {}).get("coordinates")
    if parcel.geometry.get("type") != "Polygon" or not coordinates:
        raise HTTPException(status_code=422, detail="geometry must be a GeoJSON Polygon")

    ring = coordinates[0]
    if len(ring) < 4:
        raise HTTPException(status_code=422, detail="A polygon ring needs at least four points")

    latitude, longitude = polygon_centroid(ring)
    score = restoration_potential(
        parcel.land_cover_class or "", parcel.canopy_cover, parcel.confidence
    )

    row = LandParcelDB(
        name=parcel.name,
        zone=parcel.zone,
        geometry=geometry_to_json(parcel.geometry),
        centroid_latitude=latitude,
        centroid_longitude=longitude,
        area_hectares=polygon_area_hectares(ring),
        land_cover_class=parcel.land_cover_class,
        canopy_cover=parcel.canopy_cover,
        confidence=parcel.confidence,
        restoration_potential=score.value,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return _parcel_to_schema(row)


@app.get("/api/b2b/land-cover-classes", response_model=List[LandCoverClass])
async def land_cover_legend() -> List[LandCoverClass]:
    """The land-cover legend used to score parcels.

    `reference_tiles` counts the labelled EuroSAT examples behind each class.
    Those labels are synthetic reference data, not measurements.
    """
    from backend.services.land_service import LAND_COVER_PROFILE
    from backend.services.land_reference import reference_tile_counts

    counts = reference_tile_counts()

    return [
        LandCoverClass(
            name=name,
            headroom=headroom,
            description=description,
            reference_tiles=counts.get(name, 0),
        )
        for name, (headroom, description) in sorted(
            LAND_COVER_PROFILE.items(), key=lambda item: -item[1][0]
        )
    ]


@app.post("/api/b2b/land-parcels/{parcel_id}/analyze", response_model=LandParcel)
async def analyze_land_parcel(
    parcel_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> LandParcel:
    """Score a parcel from satellite imagery and store the result."""
    from backend.pipelines.satellite_inference import VLMUnavailable, extract_json, run_vlm
    from backend.services.land_service import restoration_potential

    row = db.query(LandParcelDB).filter(LandParcelDB.id == parcel_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Parcel not found")

    path = await save_upload_temp(image)
    try:
        raw = await run_in_threadpool(run_vlm, path, row.land_cover_class)
    except VLMUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        if os.path.exists(path):
            os.remove(path)

    result = extract_json(raw)
    if result is None:
        raise HTTPException(status_code=502, detail="The vision model returned no readable JSON.")

    row.vegetation_density = result.get("vegetation_density")
    row.canopy_cover = result.get("canopy_cover")
    row.est_biomass = result.get("est_biomass")
    row.carbon_eq = result.get("carbon_EQ")
    row.restoration_quality = result.get("restoration_quality")
    row.confidence = result.get("confidence")
    row.restoration_potential = restoration_potential(
        row.land_cover_class or "", row.canopy_cover, row.confidence
    ).value
    row.analyzed_at = datetime.datetime.now(datetime.timezone.utc)

    db.commit()
    db.refresh(row)

    return _parcel_to_schema(row)


# ── Leaf diagnosis ────────────────────────────────────────────────────────────

@app.post("/api/plants/{plant_id}/diagnose", response_model=DiagnosisResponse)
async def diagnose_plant(
    plant_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DiagnosisResponse:
    """Classify a leaf photograph and record the result against the plant.

    Returns 503 while no trained checkpoint is present rather than inventing a
    diagnosis.
    """
    from backend.services.vision_service import DiagnosisUnavailable, diagnose_image

    plant = db.query(PlantDB).filter(PlantDB.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    payload = await image.read()
    if not payload:
        raise HTTPException(status_code=422, detail="The uploaded image is empty")

    try:
        from PIL import Image as PILImage

        pil_image = PILImage.open(io.BytesIO(payload))
        diagnosis = await run_in_threadpool(diagnose_image, pil_image)
    except DiagnosisUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Leaf diagnosis failed.")
        raise HTTPException(status_code=422, detail=f"Could not read the image: {exc}") from exc

    db.add(DiagnosisLogDB(
        plant_id=plant_id,
        top_class=diagnosis.top_class,
        label=diagnosis.predictions[0]["label"],
        confidence=diagnosis.confidence,
        is_defective=int(diagnosis.is_defective),
        health_score=diagnosis.health_score,
        summary=diagnosis.summary,
    ))

    # The health badge was a static seeded number; let it track the model.
    plant.health = diagnosis.health_score

    db.add(TimelineEventDB(
        plant_id=plant_id,
        date=datetime.datetime.now().strftime("%d %b"),
        event="Leaf scan",
        note=diagnosis.summary,
    ))
    db.commit()

    return DiagnosisResponse(
        plant_id=plant_id,
        predictions=diagnosis.predictions,
        top_class=diagnosis.top_class,
        label=diagnosis.predictions[0]["label"],
        confidence=diagnosis.confidence,
        is_defective=diagnosis.is_defective,
        health_score=diagnosis.health_score,
        summary=diagnosis.summary,
    )


# ── Device Manager B2B Endpoints ──────────────────────────────────────────────

@app.get("/api/b2b/devices", response_model=List[IotNode])
async def get_devices(db: Session = Depends(get_db)):
    return db.query(IotNodeDB).all()

@app.post("/api/b2b/devices", response_model=IotNode)
async def create_device(node: IotNodeCreate, db: Session = Depends(get_db)):
    # Node ids look like "NODE-8472".
    new_id = f"NODE-{random.randint(1000, 9999)}"
    
    new_node = IotNodeDB(
        id=new_id,
        zone=node.zone,
        battery=100,
        moisture=random.randint(40, 80),
        status="ok",
        latitude=node.latitude,
        longitude=node.longitude
    )
    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    return new_node

@app.post("/api/b2b/devices/{node_id}/diagnose")
async def diagnose_device(node_id: str):
    return {"message": f"Diagnostics initiated for {node_id}"}

@app.post("/api/b2b/procurement")
async def order_probes():
    return {"message": "Order placed successfully"}

@app.post("/api/b2b/maintenance")
async def request_maintenance():
    return {"message": "Maintenance ticket created"}

@app.get("/api/b2b/agents/log", response_model=List[TacticalLog])
async def get_tactical_logs(db: Session = Depends(get_db)):
    logs = db.query(TacticalLogDB).order_by(TacticalLogDB.id.desc()).limit(10).all()
    # Fall back to sample rows so the activity feed is never blank.
    if not logs:
        return [
            {"id": 1, "time": "10:42", "action": "Auto-adjusted irrigation in South Sector B", "severity": "info"},
            {"id": 2, "time": "11:15", "action": "Flagged NODE-2199 battery low", "severity": "warn"},
        ]
    return logs

async def save_upload_temp(upload_file: UploadFile) -> str:
    """Write an upload to a temporary file and return its path.

    The caller is responsible for deleting the file.
    """
    suffix = os.path.splitext(upload_file.filename or "")[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(await upload_file.read())
        return temp.name


def _metric_delta(current: dict, previous: dict, key: str) -> Optional[float]:
    """Difference in one metric between two analyses, when both reported it."""
    new_value, old_value = current.get(key), previous.get(key)

    if isinstance(new_value, (int, float)) and isinstance(old_value, (int, float)):
        return round(new_value - old_value, 3)

    return None


@app.post("/api/b2b/satellite/analyze", response_model=EuroSatAnalysisResponse)
async def analyze_satellite_images(
    pre_restoration: UploadFile = File(...),
    current_state: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> EuroSatAnalysisResponse:
    """Compare a baseline and a current satellite image of the same site.

    Both images are scored by a vision-language model; the response carries the
    current metrics plus the change against the baseline.
    """
    from backend.pipelines.satellite_inference import extract_json, run_vlm

    temp_paths: List[str] = []

    try:
        pre_path = await save_upload_temp(pre_restoration)
        temp_paths.append(pre_path)

        current_path = await save_upload_temp(current_state)
        temp_paths.append(current_path)

        # The model call is blocking, so keep it off the event loop.
        pre_raw = await run_in_threadpool(run_vlm, pre_path, "before restoration")
        current_raw = await run_in_threadpool(run_vlm, current_path, "after restoration")

        current_result = extract_json(current_raw)
        if current_result is None:
            raise HTTPException(
                status_code=502,
                detail="The vision model did not return readable JSON.",
            )

        pre_result = extract_json(pre_raw) or {}

        delta = None
        if pre_result:
            delta = {
                "canopy_cover_change": _metric_delta(current_result, pre_result, "canopy_cover"),
                "biomass_change": _metric_delta(current_result, pre_result, "est_biomass"),
                "carbon_change": _metric_delta(current_result, pre_result, "carbon_EQ"),
            }

        labels = {
            "vegetation_density": current_result.get("vegetation_density"),
            "canopy_cover": current_result.get("canopy_cover"),
            "est_biomass": current_result.get("est_biomass"),
            "carbon_eq": current_result.get("carbon_EQ"),
            "restoration_quality": current_result.get("restoration_quality"),
            "confidence": current_result.get("confidence"),
            "restoration_delta": delta,
        }

        db.add(SatelliteAnalysisLogDB(
            image_path=current_state.filename or "",
            pre_image_path=pre_restoration.filename or "",
            class_name="Satellite Restoration Analysis",
            vegetation_density=labels["vegetation_density"],
            canopy_cover=labels["canopy_cover"],
            est_biomass=labels["est_biomass"],
            carbon_eq=labels["carbon_eq"],
            restoration_quality=labels["restoration_quality"],
            confidence=labels["confidence"],
            canopy_cover_change=(delta or {}).get("canopy_cover_change"),
            biomass_change=(delta or {}).get("biomass_change"),
            carbon_change=(delta or {}).get("carbon_change"),
        ))
        db.commit()

        return EuroSatAnalysisResponse(
            image_path=current_state.filename or "",
            class_name="Satellite Restoration Analysis",
            labels=labels,
        )

    except HTTPException:
        # Already carries a meaningful status; do not re-wrap it as a 500.
        raise
    except Exception as exc:
        logger.exception("Satellite analysis failed.")
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        # Runs on every path, so a model failure no longer leaks temp files.
        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)


@app.get("/api/b2b/satellite/history", response_model=List[SatelliteAnalysis])
async def satellite_history(
    limit: int = 20,
    db: Session = Depends(get_db),
) -> List[SatelliteAnalysisLogDB]:
    """Return the most recent satellite analyses, newest first."""
    return (
        db.query(SatelliteAnalysisLogDB)
        .order_by(SatelliteAnalysisLogDB.id.desc())
        .limit(min(limit, 100))
        .all()
    )
