import datetime
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from backend.pipelines.main.nodes.nodes import graph_app
import os
import tempfile

from backend.pipelines.satellite_inference import run_vlm, extract_json

# Import dari schema.py dan db.py yang sudah disesuaikan
from .schema import ChatRequest, ChatResponse, WeatherMacroResponse, WeatherAlertResponse, Plant, ScannedItem, PlantCreate, IotNode, IotNodeCreate, TacticalLog, EuroSatAnalysisResponse
from .db import get_db, init_seed_data, ChatLog, WeatherLog, PlantDB, ScannedItemDB, ProbeDataDB, TimelineEventDB, IotNodeDB, TacticalLogDB
import random


app = FastAPI(title="Cognitive Assistant API")

# Saat aplikasi dijalankan, kita seed (isi) SQLite dengan data Plant ID 1 
# agar frontend tidak blank saat memanggil GET /api/plants/1
@app.on_event("startup")
def on_startup():
    init_seed_data()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# ── Chat Endpoint ──────────────────────────────────────────────────────────────

# Menangani dua URL (dari struktur asli b2c, maupun dari permintaan spesifik tanaman frontend)
@app.post("/api/b2c/chat", response_model=ChatResponse)
@app.post("/api/plants/{plant_id}/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, plant_id: int = None, db: Session = Depends(get_db)):
    # Di schema.py terbaru, ChatRequest menggunakan 'messages' (Array), bukan 'text' statis.
    # Kita ambil pesan terakhir dari user:
    user_text = request.messages[-1].content.lower() if request.messages else ""
    
    # # Custom respon berdasarkan kata kunci (untuk simulasi)
    # if "siram" in user_text or "water" in user_text:
    #     bot_reply = "Kelembapan tanah berada di tingkat optimal. Anda tidak perlu menyiramnya hari ini."
    # elif "gambar" in user_text or "kamera" in user_text or "foto" in user_text:
    #     bot_reply = "Berdasarkan analisis visual, daun terlihat sehat dengan warna yang merata. Tidak ada tanda-tanda hama. Lanjutkan rutinitas saat ini! ✨"
    # else:
    #     bot_reply = "Got it. I've cross-checked your plant against 12k similar cases. Adjusting your care plan now."

    result = graph_app.invoke({
        "user_query": user_text
    })

    bot_reply = result["final_answer"]
    
    bot_tags = [
        "GraphRAG",
        "DeepSeek-R1 Reasoning"
    ]

    # Menentukan ID tanaman yang dibicarakan
    pid = plant_id or request.plant_id

    # Simpan ke Database
    new_log = ChatLog(
        plant_id=pid,
        user_message=user_text,
        bot_response=bot_reply
    )
    db.add(new_log)
    db.commit()
    
    return ChatResponse(
        role="assistant",
        text=bot_reply,
        tags=bot_tags
    )

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

async def save_upload_temp(upload_file: UploadFile):

    suffix = os.path.splitext(
        upload_file.filename
    )[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp:

        content = await upload_file.read()

        temp.write(content)

        return temp.name




@app.post("/api/b2b/satellite/analyze", response_model=EuroSatAnalysisResponse)
async def analyze_satellite_images(
    pre_restoration: UploadFile = File(...),
    current_state: UploadFile = File(...)
):
    try:

        # ====================================================
        # SAVE FILES TEMPORARILY
        # ====================================================

        pre_path = await save_upload_temp(
            pre_restoration
        )

        current_path = await save_upload_temp(
            current_state
        )

        # ====================================================
        # RUN INFERENCE
        # ====================================================

        pre_result_raw = run_vlm(
            pre_path,
            class_hint="before restoration"
        )

        current_result_raw = run_vlm(
            current_path,
            class_hint="after restoration"
        )

        # ====================================================
        # PARSE JSON
        # ====================================================

        pre_result = extract_json(
            pre_result_raw
        )

        current_result = extract_json(
            current_result_raw
        )

        if current_result is None:

            raise HTTPException(
                status_code=500,
                detail="Failed to parse VLM output"
            )

        # ====================================================
        # OPTIONAL RESTORATION COMPARISON
        # ====================================================

        restoration_delta = None

        if pre_result and current_result:

            restoration_delta = {

                "canopy_cover_change": round(
                    current_result.get("canopy_cover", 0)
                    - pre_result.get("canopy_cover", 0),
                    3
                ),

                "biomass_change": round(
                    current_result.get("est_biomass", 0)
                    - pre_result.get("est_biomass", 0),
                    3
                ),

                "carbon_change": round(
                    current_result.get("carbon_EQ", 0)
                    - pre_result.get("carbon_EQ", 0),
                    3
                )
            }

        # ====================================================
        # CLEANUP TEMP FILES
        # ====================================================

        if os.path.exists(pre_path):
            os.remove(pre_path)

        if os.path.exists(current_path):
            os.remove(current_path)

        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "image_path": current_state.filename,

            "class_name": "Satellite Restoration Analysis",

            "labels": {

                "vegetation_density":
                    current_result.get(
                        "vegetation_density"
                    ),

                "canopy_cover":
                    current_result.get(
                        "canopy_cover"
                    ),

                "est_biomass":
                    current_result.get(
                        "est_biomass"
                    ),

                "carbon_EQ":
                    current_result.get(
                        "carbon_EQ"
                    ),

                "restoration_quality":
                    current_result.get(
                        "restoration_quality"
                    ),

                "confidence":
                    current_result.get(
                        "confidence"
                    ),

                "restoration_delta":
                    restoration_delta
            }
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )