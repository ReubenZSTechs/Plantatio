"""SQLAlchemy models, engine and session management for the Plantatio API."""

import datetime

from sqlalchemy import (
    create_engine, Column, BigInteger, Integer, String,
    Float, DateTime, ForeignKey, Text
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from app.config import settings

DATABASE_URL = settings.database_url


# ── SQLAlchemy Engine ─────────────────────────────────────────────────────────
_engine_options: dict = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    _engine_options["connect_args"] = {"check_same_thread": False}
else:
    _engine_options.update(pool_size=5, max_overflow=10)

engine = create_engine(DATABASE_URL, **_engine_options)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# SQLite only auto-increments INTEGER PRIMARY KEY, not BIGINT, so a plain
# BigInteger surrogate key fails to insert there. Using a variant keeps 64-bit
# ids on Postgres while staying portable for local runs and tests.
PrimaryKey = BigInteger().with_variant(Integer, "sqlite")
ForeignKeyType = BigInteger().with_variant(Integer, "sqlite")


def _utc_now() -> datetime.datetime:
    """Current UTC time, used as the default for timestamp columns."""
    return datetime.datetime.now(datetime.timezone.utc)


Base = declarative_base()

# ── Models ─────────────────────────────────────────────────────────────────────

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(PrimaryKey, primary_key=True, index=True, autoincrement=True)
    plant_id = Column(ForeignKeyType, ForeignKey("plants.id"), nullable=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=_utc_now)


class WeatherLog(Base):
    __tablename__ = "weather_logs"

    id = Column(PrimaryKey, primary_key=True, index=True, autoincrement=True)
    city = Column(String(100), nullable=False)
    tempC = Column(Float, nullable=False)
    condition = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=_utc_now)


class PlantDB(Base):
    __tablename__ = "plants"

    id = Column(PrimaryKey, primary_key=True, index=True, autoincrement=True)
    nickname = Column(String(100), nullable=False)
    species = Column(String(200), default="")
    image = Column(Text, default="")
    health = Column(Float, default=100.0)
    days_planted = Column(Integer, default=0)

    probe = relationship(
        "ProbeDataDB", back_populates="plant",
        uselist=False, cascade="all, delete-orphan"
    )
    timeline = relationship(
        "TimelineEventDB", back_populates="plant",
        cascade="all, delete-orphan"
    )
    scanned_items = relationship(
        "ScannedItemDB", back_populates="plant",
        cascade="all, delete-orphan"
    )


class ProbeDataDB(Base):
    __tablename__ = "probe_data"

    id = Column(PrimaryKey, primary_key=True, index=True, autoincrement=True)
    plant_id = Column(ForeignKeyType, ForeignKey("plants.id"), unique=True)
    moisture = Column(Float, default=50.0)
    nutrients = Column(Float, default=50.0)
    light = Column(Float, default=60.0)
    temperature = Column(Float, default=24.0)

    plant = relationship("PlantDB", back_populates="probe")


class TimelineEventDB(Base):
    __tablename__ = "timeline_events"

    id = Column(PrimaryKey, primary_key=True, index=True, autoincrement=True)
    plant_id = Column(ForeignKeyType, ForeignKey("plants.id"))
    date = Column(String(50), nullable=False)
    event = Column(String(200), nullable=False)
    note = Column(Text, nullable=False)
    scan_category = Column(String(50), nullable=True)

    plant = relationship("PlantDB", back_populates="timeline")


class ScannedItemDB(Base):
    __tablename__ = "scanned_items"

    # ID tetap String karena frontend pakai format seperti "PRB-1234"
    id = Column(String(50), primary_key=True, index=True)
    plant_id = Column(ForeignKeyType, ForeignKey("plants.id"))
    category = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    brand = Column(String(200), nullable=True)
    sensor_id = Column(String(100), nullable=True)
    seed_variety = Column(String(200), nullable=True)
    germination_days = Column(Integer, nullable=True)
    soil_type = Column(String(100), nullable=True)
    ph_level = Column(Float, nullable=True)
    npk_ratio = Column(String(50), nullable=True)
    application_frequency = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    scanned_at = Column(String(50), nullable=False)

    plant = relationship("PlantDB", back_populates="scanned_items")


class IotNodeDB(Base):
    __tablename__ = "iot_nodes"

    # ID tetap String karena pakai format "NODE-1042"
    id = Column(String(50), primary_key=True, index=True)
    zone = Column(String(200), nullable=False)
    battery = Column(Integer, default=100)
    moisture = Column(Integer, default=50)
    status = Column(String(50), default="ok")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


class TacticalLogDB(Base):
    __tablename__ = "tactical_logs"

    id = Column(PrimaryKey, primary_key=True, index=True, autoincrement=True)
    time = Column(String(10), nullable=False)
    action = Column(Text, nullable=False)
    severity = Column(String(20), default="info")


class LandParcelDB(Base):
    """A candidate restoration site.

    Geometry is stored as a GeoJSON Polygon so a parcel describes an area
    rather than a point; the IoT node tables remain point-based.
    """

    __tablename__ = "land_parcels"

    id = Column(PrimaryKey, primary_key=True, index=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    zone = Column(String(80))
    geometry = Column(Text, nullable=False)
    centroid_latitude = Column(Float, nullable=False)
    centroid_longitude = Column(Float, nullable=False)
    area_hectares = Column(Float)
    land_cover_class = Column(String(80))
    vegetation_density = Column(String(50))
    canopy_cover = Column(Float)
    est_biomass = Column(Float)
    carbon_eq = Column(Float)
    restoration_quality = Column(String(50))
    confidence = Column(Float)
    restoration_potential = Column(Float, index=True)
    analyzed_at = Column(DateTime)
    created_at = Column(DateTime, default=_utc_now)


class DiagnosisLogDB(Base):
    """A stored leaf-disease classification for one plant."""

    __tablename__ = "diagnosis_logs"

    id = Column(PrimaryKey, primary_key=True, index=True, autoincrement=True)
    plant_id = Column(ForeignKeyType, ForeignKey("plants.id"))
    top_class = Column(String(120), nullable=False)
    label = Column(String(120))
    confidence = Column(Float)
    is_defective = Column(Integer, default=0)
    health_score = Column(Float)
    summary = Column(Text)
    timestamp = Column(DateTime, default=_utc_now)


class SatelliteAnalysisLogDB(Base):
    __tablename__ = "satellite_analysis_logs"

    id = Column(PrimaryKey, primary_key=True, index=True, autoincrement=True)
    image_path = Column(Text, nullable=False)
    pre_image_path = Column(Text)
    class_name = Column(String(100), nullable=False)
    vegetation_density = Column(String(50))
    canopy_cover = Column(Float)
    est_biomass = Column(Float)
    carbon_eq = Column(Float)
    restoration_quality = Column(String(50))
    confidence = Column(Float)
    canopy_cover_change = Column(Float)
    biomass_change = Column(Float)
    carbon_change = Column(Float)
    timestamp = Column(DateTime, default=_utc_now)


# ── Schema and session helpers ────────────────────────────────────────────────

def create_tables() -> None:
    """Create any missing tables.

    Called from the application lifespan rather than at import, so importing
    this module never opens a database connection.
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """Yield a request-scoped session, closing it when the request ends."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_land_parcels(db) -> int:
    """Create demo restoration parcels around the monitored site.

    Anchored to the same Jakarta coordinates as the seeded IoT fleet, so the
    map shows parcels and sensors in one coherent place. The EuroSAT corpus in
    misc/ supplies the land-cover vocabulary but carries no coordinates, so it
    is not used to place anything.
    """
    from backend.services.land_service import (
        geometry_to_json, polygon_area_hectares, polygon_centroid,
        restoration_potential, square_around,
    )

    if db.query(LandParcelDB).first():
        return 0

    # (name, zone, lat, lon, size_m, land cover, canopy, biomass, carbon, confidence)
    demo_parcels = [
        ("Northern Grazing Strip", "North Sector A", -6.1746, 106.8285, 900,
         "Pasture", 0.08, 0.12, 0.05, 0.88),
        ("Southern Scrub Margin", "South Sector B", -6.1792, 106.8198, 750,
         "HerbaceousVegetation", 0.18, 0.22, 0.11, 0.81),
        ("Riverside Buffer", "South Sector B", -6.1771, 106.8232, 500,
         "River", 0.05, 0.08, 0.03, 0.74),
        ("East Field Rotation", "East Sector C", -6.1733, 106.8321, 1100,
         "AnnualCrop", 0.26, 0.34, 0.18, 0.86),
        ("Greenhouse Verge", "Main Greenhouse", -6.1714, 106.8296, 400,
         "PermanentCrop", 0.42, 0.48, 0.3, 0.79),
        ("Established Woodlot", "North Sector A", -6.1709, 106.8258, 850,
         "Forest", 0.88, 0.91, 0.76, 0.93),
    ]

    for (name, zone, lat, lon, size, cover, canopy, biomass, carbon, confidence) in demo_parcels:
        geometry = square_around(lat, lon, size)
        ring = geometry["coordinates"][0]
        centroid_lat, centroid_lon = polygon_centroid(ring)
        score = restoration_potential(cover, canopy, confidence)

        db.add(LandParcelDB(
            name=name,
            zone=zone,
            geometry=geometry_to_json(geometry),
            centroid_latitude=centroid_lat,
            centroid_longitude=centroid_lon,
            area_hectares=polygon_area_hectares(ring),
            land_cover_class=cover,
            vegetation_density="high" if canopy > 0.6 else "medium" if canopy > 0.2 else "low",
            canopy_cover=canopy,
            est_biomass=biomass,
            carbon_eq=carbon,
            restoration_quality="strong" if canopy > 0.6 else "moderate" if canopy > 0.2 else "poor",
            confidence=confidence,
            restoration_potential=score.value,
        ))

    db.commit()
    return len(demo_parcels)


def init_seed_data():
    """Populate demo rows for any table that is still empty."""
    db = SessionLocal()
    seed_land_parcels(db)

    # Seed Plant
    if not db.query(PlantDB).filter(PlantDB.id == 1).first():
        new_plant = PlantDB(
            id=1,
            nickname="Tomato",
            species="Solanum lycopersicum",
            image="https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=600&q=80",
            health=85.0,
            days_planted=14,
        )
        db.add(new_plant)
        db.commit()
        db.add(ProbeDataDB(
            plant_id=1, moisture=45.0, nutrients=60.0,
            light=80.0, temperature=26.0
        ))
        db.add_all([
            TimelineEventDB(plant_id=1, date="10 Oct", event="Planted", note="Seedling moved into its pot"),
            TimelineEventDB(plant_id=1, date="12 Oct", event="Watered", note="First watering"),
        ])
        db.commit()

    # Seed IoT Nodes
    if not db.query(IotNodeDB).first():
        db.add_all([
            IotNodeDB(id="NODE-1042", zone="North Sector A",   battery=85, moisture=62, status="ok",       latitude=-6.1754, longitude=106.8272),
            IotNodeDB(id="NODE-2199", zone="South Sector B", battery=12, moisture=28, status="critical", latitude=-6.1780, longitude=106.8210),
            IotNodeDB(id="NODE-3011", zone="Main Greenhouse",   battery=45, moisture=50, status="warn",     latitude=-6.1720, longitude=106.8300),
        ])
        db.commit()

    # Seed Tactical Logs
    if not db.query(TacticalLogDB).first():
        db.add_all([
            TacticalLogDB(time="10:42", action="Auto-adjusted irrigation in South Sector B",  severity="info"),
            TacticalLogDB(time="11:15", action="Flagged NODE-2199 battery low",    severity="warn"),
            TacticalLogDB(time="11:30", action="Halted fertigation (High wind risk)", severity="critical"),
        ])
        db.commit()

    db.close()