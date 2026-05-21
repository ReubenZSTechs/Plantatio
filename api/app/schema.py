from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from typing import List, Optional, Literal


# ── Base Model ─────────────────────────────────────────────────────────────────
# Otomatis mengubah snake_case (Python) ↔ camelCase (JSON/Frontend)
class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,   # wajib untuk SQLAlchemy ORM → Pydantic
    )


# ── Types ──────────────────────────────────────────────────────────────────────

ScanCategory = Literal["sensor", "seed", "soil", "fertilizer", "other"]


# ── Chat ───────────────────────────────────────────────────────────────────────

class ChatMessage(CamelModel):
    role: str
    content: str

class ChatRequest(CamelModel):
    messages: List[ChatMessage]
    plant_id: Optional[int] = None

class ChatResponse(CamelModel):
    role: str
    text: str
    tags: Optional[List[str]] = None


# ── Weather ────────────────────────────────────────────────────────────────────

class ForecastItem(CamelModel):
    day: str
    icon: str
    temp_c: int                 # → tempC di JSON

class WeatherMacroResponse(CamelModel):
    city: str
    temp_c: int                 # → tempC di JSON
    condition: str
    humidity: int
    forecast: List[ForecastItem]

class WeatherAlertResponse(CamelModel):
    title: str
    body: str


# ── Probe ──────────────────────────────────────────────────────────────────────

class ProbeData(CamelModel):
    moisture: float = 50
    nutrients: float = 50
    light: float = 60
    temperature: float = 24


# ── Scanned Item ───────────────────────────────────────────────────────────────

class ScannedItemCreate(CamelModel):
    category: ScanCategory
    name: str
    brand: Optional[str] = None
    sensor_id: Optional[str] = None
    seed_variety: Optional[str] = None
    germination_days: Optional[int] = None
    soil_type: Optional[str] = None
    ph_level: Optional[float] = None
    npk_ratio: Optional[str] = None
    application_frequency: Optional[str] = None
    description: Optional[str] = None

class ScannedItem(ScannedItemCreate):
    id: str                     # Format "PRB-1234", "SEED-001", dll.
    plant_id: Optional[int] = None
    scanned_at: str


# ── Timeline ───────────────────────────────────────────────────────────────────

class TimelineEvent(CamelModel):
    id: Optional[int] = None
    plant_id: Optional[int] = None
    date: str
    event: str
    note: str
    scan_category: Optional[ScanCategory] = None


# ── Plant ──────────────────────────────────────────────────────────────────────

class PlantCreate(CamelModel):
    nickname: str
    species: Optional[str] = ""
    image: Optional[str] = ""

class PlantUpdate(CamelModel):
    nickname: Optional[str] = None
    species: Optional[str] = None
    image: Optional[str] = None

class Plant(CamelModel):
    id: int
    nickname: str
    species: str
    image: str
    health: float
    days_planted: int           # → daysPlanted di JSON
    probe: ProbeData
    timeline: List[TimelineEvent] = []
    scanned_items: List[ScannedItem] = []   # → scannedItems di JSON


# ── IoT Devices & Tactical ─────────────────────────────────────────────────────

class IotNodeCreate(CamelModel):
    zone: str
    latitude: float
    longitude: float

class IotNode(CamelModel):
    id: str
    zone: str
    battery: int
    moisture: int
    status: str
    latitude: float
    longitude: float

class TacticalLog(CamelModel):
    id: int
    time: str
    action: str
    severity: str               # "info" | "warn" | "critical"


# ── Satellite ML Analysis (EuroSAT) ───────────────────────────────────────────

class MLLabels(CamelModel):
    vegetation_density: str
    canopy_cover: float
    est_biomass: float
    carbon_eq: float = Field(alias="carbon_EQ")
    restoration_quality: str
    confidence: float

class EuroSatAnalysisResponse(CamelModel):
    image_path: str
    class_name: str
    labels: MLLabels