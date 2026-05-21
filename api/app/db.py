import datetime
from sqlalchemy import (
    create_engine, Column, BigInteger, Integer, String,
    Float, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from urllib.parse import quote_plus

# ── Konfigurasi Database (Supabase Transaction Pooler) ─────────────────────────
raw_password = "PlantatioP4ss1231"          # password BARU
project_ref = "bfuzqnvyauqxudqmczmq"
db_user = f"postgres.{project_ref}"

encoded_password = quote_plus(str(raw_password))

DATABASE_URL = (
    "postgresql+psycopg2://"
    f"{db_user}:{encoded_password}"
    "@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
    "?sslmode=require"
)

# ── SQLAlchemy Engine ─────────────────────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,        # aman untuk pooler
    max_overflow=10,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

# ── Models ─────────────────────────────────────────────────────────────────────

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    plant_id = Column(BigInteger, ForeignKey("plants.id"), nullable=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class WeatherLog(Base):
    __tablename__ = "weather_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    city = Column(String(100), nullable=False)
    tempC = Column(Float, nullable=False)
    condition = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class PlantDB(Base):
    __tablename__ = "plants"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
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

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    plant_id = Column(BigInteger, ForeignKey("plants.id"), unique=True)
    moisture = Column(Float, default=50.0)
    nutrients = Column(Float, default=50.0)
    light = Column(Float, default=60.0)
    temperature = Column(Float, default=24.0)

    plant = relationship("PlantDB", back_populates="probe")


class TimelineEventDB(Base):
    __tablename__ = "timeline_events"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    plant_id = Column(BigInteger, ForeignKey("plants.id"))
    date = Column(String(50), nullable=False)
    event = Column(String(200), nullable=False)
    note = Column(Text, nullable=False)
    scan_category = Column(String(50), nullable=True)

    plant = relationship("PlantDB", back_populates="timeline")


class ScannedItemDB(Base):
    __tablename__ = "scanned_items"

    # ID tetap String karena frontend pakai format seperti "PRB-1234"
    id = Column(String(50), primary_key=True, index=True)
    plant_id = Column(BigInteger, ForeignKey("plants.id"))
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

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    time = Column(String(10), nullable=False)
    action = Column(Text, nullable=False)
    severity = Column(String(20), default="info")


class SatelliteAnalysisLogDB(Base):
    __tablename__ = "satellite_analysis_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    image_path = Column(Text, nullable=False)
    class_name = Column(String(100), nullable=False)
    vegetation_density = Column(String(50))
    canopy_cover = Column(Float)
    est_biomass = Column(Float)
    carbon_eq = Column(Float)
    restoration_quality = Column(String(50))
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


# ── Buat Semua Tabel (jalankan sekali saat startup) ────────────────────────────
Base.metadata.create_all(bind=engine)


# ── Utilitas ───────────────────────────────────────────────────────────────────

def get_db():
    """Dependency injection untuk FastAPI route."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_seed_data():
    """Isi data awal jika tabel masih kosong."""
    db = SessionLocal()

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
            TimelineEventDB(plant_id=1, date="10 Oct", event="Ditanam", note="Bibit dipindahkan ke pot"),
            TimelineEventDB(plant_id=1, date="12 Oct", event="Disiram", note="Penyiraman pertama"),
        ])
        db.commit()

    # Seed IoT Nodes
    if not db.query(IotNodeDB).first():
        db.add_all([
            IotNodeDB(id="NODE-1042", zone="Sektor A - Utara",   battery=85, moisture=62, status="ok",       latitude=-6.1754, longitude=106.8272),
            IotNodeDB(id="NODE-2199", zone="Sektor B - Selatan", battery=12, moisture=28, status="critical", latitude=-6.1780, longitude=106.8210),
            IotNodeDB(id="NODE-3011", zone="Greenhouse Utama",   battery=45, moisture=50, status="warn",     latitude=-6.1720, longitude=106.8300),
        ])
        db.commit()

    # Seed Tactical Logs
    if not db.query(TacticalLogDB).first():
        db.add_all([
            TacticalLogDB(time="10:42", action="Auto-adjust irrigation Sektor B",  severity="info"),
            TacticalLogDB(time="11:15", action="Flagged NODE-2199 battery low",    severity="warn"),
            TacticalLogDB(time="11:30", action="Halted fertigation (High wind risk)", severity="critical"),
        ])
        db.commit()

    db.close()