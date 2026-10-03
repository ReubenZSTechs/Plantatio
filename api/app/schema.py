from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


# ── Base model ────────────────────────────────────────────────────────────────

class CamelModel(BaseModel):
    """Maps Python snake_case to the camelCase the frontend expects.

    `from_attributes` lets SQLAlchemy rows serialise directly.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


# ── Types ──────────────────────────────────────────────────────────────────────

ScanCategory = Literal["sensor", "seed", "soil", "fertilizer", "other"]


# ── Chat ──────────────────────────────────────────────────────────────────────

ChatScope = Literal["b2c", "b2b", "plant"]


class ChatMessage(CamelModel):
    """One turn in the conversation."""

    role: str
    content: str


class ChatRequest(CamelModel):
    """A chat turn plus the context it should be answered in."""

    messages: List[ChatMessage]
    plant_id: Optional[int] = None
    scope: ChatScope = "b2c"


class GraphProvenance(CamelModel):
    """What the agent retrieved on the way to its answer.

    Surfaced so the UI can show real sources instead of decorative badges.
    """

    sub_questions: List[str] = []
    retrieved_facts: List[str] = []
    record_count: int = 0
    graph_available: bool = True


class ChatResponse(CamelModel):
    """The assistant's reply and the evidence behind it."""

    role: str
    text: str
    tags: Optional[List[str]] = None
    provenance: Optional[GraphProvenance] = None


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

class RestorationDelta(CamelModel):
    """Change between the baseline and current images."""

    canopy_cover_change: Optional[float] = None
    biomass_change: Optional[float] = None
    carbon_change: Optional[float] = None


class MLLabels(CamelModel):
    """Ecological metrics estimated from one satellite image.

    Every field is optional: these come from a vision-language model that may
    omit keys, and a missing value should not turn into a 500.
    """

    vegetation_density: Optional[str] = None
    canopy_cover: Optional[float] = None
    est_biomass: Optional[float] = None
    # No alias here. `Field(alias="carbon_EQ")` overrode the camelCase
    # generator, so the response carried `carbon_EQ` while the frontend read
    # `carbonEq` and the tile rendered blank.
    carbon_eq: Optional[float] = None
    restoration_quality: Optional[str] = None
    confidence: Optional[float] = None
    restoration_delta: Optional[RestorationDelta] = None


class EuroSatAnalysisResponse(CamelModel):
    """Result of comparing a baseline and a current satellite image."""

    image_path: str
    class_name: str
    labels: MLLabels


class SatelliteAnalysis(CamelModel):
    """A stored satellite analysis, as returned by the history endpoint."""

    id: int
    image_path: str
    pre_image_path: Optional[str] = None
    class_name: str
    vegetation_density: Optional[str] = None
    canopy_cover: Optional[float] = None
    est_biomass: Optional[float] = None
    carbon_eq: Optional[float] = None
    restoration_quality: Optional[str] = None
    confidence: Optional[float] = None
    canopy_cover_change: Optional[float] = None
    biomass_change: Optional[float] = None
    carbon_change: Optional[float] = None
    timestamp: Optional[datetime] = None