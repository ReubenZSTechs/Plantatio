"""HTTP surface for Plantatio: plants, telemetry, devices and the AI agent."""

import datetime
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
    SatelliteAnalysisLogDB, TimelineEventDB, WeatherLog, create_tables, get_db,
    init_seed_data,
)
from .schema import (
    ChatRequest, ChatResponse, EuroSatAnalysisResponse, GraphProvenance,
    IotNode, IotNodeCreate, Plant, PlantCreate, SatelliteAnalysis, ScannedItem,
    TacticalLog,
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
        city="Kawasan Restorasi, Jakarta",
        tempC=32.0,
        condition="Cerah Berawan"
    )
    db.add(new_log)
    db.commit()

    # Menggunakan temp_c sesuai properti Pydantic (diubah otomatis ke tempC oleh CamelModel di schema)
    return WeatherMacroResponse(
        city="Kawasan Restorasi, Jakarta",
        temp_c=32,
        condition="Cerah Berawan",
        humidity=65,
        forecast=[
            {"day": "Sen", "icon": "sun", "temp_c": 33},
            {"day": "Sel", "icon": "cloud", "temp_c": 31},
            {"day": "Rab", "icon": "rain", "temp_c": 28},
            {"day": "Kam", "icon": "rain", "temp_c": 27},
            {"day": "Jum", "icon": "cloud", "temp_c": 30},
        ]
    )

@app.get("/api/v1/weather/alert", response_model=WeatherAlertResponse)
async def get_weather_alert():
    return WeatherAlertResponse(
        title="Peringatan Cekaman Panas (Heat Stress)",
        body="Suhu makro melebihi ambang batas adaptasi tanaman muda. Sistem AI menyarankan pengaktifan naungan."
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
        raise HTTPException(status_code=404, detail="Tanaman tidak ditemukan")
    return plant

@app.post("/api/plants/{plant_id}/scan", response_model=Plant)
async def scan_item(plant_id: int, item: ScannedItem, db: Session = Depends(get_db)):
    plant = db.query(PlantDB).filter(PlantDB.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Tanaman tidak ditemukan")
    
    # Hapus data lama yang punya kategori sama agar tidak terjadi duplikasi "Sensor" / "Bibit" dsb
    db.query(ScannedItemDB).filter(
        ScannedItemDB.plant_id == plant_id, 
        ScannedItemDB.category == item.category
    ).delete()
    
    # Masukkan item baru
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

    # Ubah data Sensor Probe jika yang discan adalah sensor
    if item.category == "sensor" and plant.probe:
        plant.probe.moisture = 72.0
        plant.probe.nutrients = 68.0
        plant.probe.light = 85.0
        plant.probe.temperature = 24.0

    # Tambahkan event ke timeline
    event_labels = {
        "sensor": "Sensor dipasang", "seed": "Bibit dikonfirmasi", 
        "soil": "Media tanam diganti", "fertilizer": "Pupuk ditambahkan", "other": "Konteks diperbarui"
    }
    today = datetime.datetime.now().strftime("%d %b")
    
    new_timeline = TimelineEventDB(
        plant_id=plant_id,
        date=today,
        event=event_labels.get(item.category, "Item ditambahkan"),
        note=f"{item.name} ({item.brand or ''}) tersinkron ke AI",
        scan_category=item.category
    )
    db.add(new_timeline)

    # Commit semua perubahan
    db.commit()
    db.refresh(plant)
    
    # Return plant akan dikonversi menjadi JSON oleh Pydantic (di schema.py)
    return plant

# 1. GET: Ambil daftar seluruh tanaman di kebun
@app.get("/api/plants", response_model=List[Plant])
async def get_all_plants(db: Session = Depends(get_db)):
    plants = db.query(PlantDB).all()
    return plants

# 2. POST: Buat tanaman baru (saat scan bibit/sensor baru)
@app.post("/api/plants", response_model=Plant)
async def create_plant(plant_req: PlantCreate, db: Session = Depends(get_db)):
    # Buat objek tanaman baru
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

    # Secara otomatis buatkan Probe (Sensor Data) default yang kosong
    default_probe = ProbeDataDB(
        plant_id=new_plant.id,
        moisture=50.0, nutrients=50.0, light=50.0, temperature=24.0
    )
    db.add(default_probe)

    # Tambahkan timeline bahwa ia baru saja dibuat
    today = datetime.datetime.now().strftime("%d %b")
    creation_timeline = TimelineEventDB(
        plant_id=new_plant.id,
        date=today,
        event="Terdaftar",
        note="Ditambahkan via Plantatio Scanner"
    )
    db.add(creation_timeline)
    
    db.commit()
    db.refresh(new_plant)
    
    return new_plant

# 3. DELETE: Hapus tanaman
@app.delete("/api/plants/{plant_id}")
async def delete_plant(plant_id: int, db: Session = Depends(get_db)):
    plant = db.query(PlantDB).filter(PlantDB.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Tanaman tidak ditemukan")
    
    db.delete(plant)
    db.commit()
    return {"message": "Tanaman berhasil dihapus"}

# ── Device Manager B2B Endpoints ──────────────────────────────────────────────

@app.get("/api/b2b/devices", response_model=List[IotNode])
async def get_devices(db: Session = Depends(get_db)):
    return db.query(IotNodeDB).all()

@app.post("/api/b2b/devices", response_model=IotNode)
async def create_device(node: IotNodeCreate, db: Session = Depends(get_db)):
    # Generate ID acak seperti "NODE-8472"
    new_id = f"NODE-{random.randint(1000, 9999)}"
    
    new_node = IotNodeDB(
        id=new_id,
        zone=node.zone,
        battery=100, # Perangkat baru baterainya 100%
        moisture=random.randint(40, 80), # Data awal simulasi
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
    # Jika tabel kosong, kita berikan fallback default agar map berfungsi
    if not logs:
        return [
            {"id": 1, "time": "10:42", "action": "Auto-adjust irrigation Sektor B", "severity": "info"},
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
